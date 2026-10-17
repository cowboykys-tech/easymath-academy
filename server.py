#!/usr/bin/env python3
"""이지매쓰 시제품 서버: 정적 화면, 카카오 로그인, 출퇴근 승인 API."""

from __future__ import annotations

import hashlib
import hmac
import http.cookies
import json
import mimetypes
import os
import secrets
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from email import policy
from email.parser import BytesParser
from getpass import getpass
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
DB_PATH = Path(os.environ.get("ACADEMY_DB_PATH", str(DATA / "academy.sqlite3")))
PHOTO_PATH = Path(os.environ.get("ACADEMY_PHOTO_PATH", str(DATA / "photos")))
PHOTO_PATH.mkdir(parents=True, exist_ok=True)
KST = ZoneInfo("Asia/Seoul")
SESSION_COOKIE = "easymath_teacher_session"
OWNER_SESSION_COOKIE = "easymath_owner_session"
OAUTH_STATES: dict[str, float] = {}
OWNER_LOGIN_ATTEMPTS: dict[str, list[float]] = {}
SCHEDULE_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
DAY_KEYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
MAX_PHOTO_BYTES = 15 * 1024 * 1024
MAX_PHOTO_REQUEST_BYTES = 60 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/heic": ".heic",
    "image/heif": ".heif",
}
OWNER_PASSWORD_ITERATIONS = 600_000
KAKAO_SEND_LOCK = threading.Lock()
CODEX_FEEDBACK_LOCK = threading.Lock()
KIOSK_PAIR_ATTEMPTS: dict[str, list[float]] = {}
KIOSK_CHECKIN_ATTEMPTS: dict[str, list[float]] = {}


def now_kst() -> datetime:
    return datetime.now(KST)


def iso_now() -> str:
    return now_kst().isoformat(timespec="seconds")


def db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def ensure_sunday_work_schedule(connection: sqlite3.Connection) -> None:
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='teacher_work_schedule'"
    ).fetchone()
    if not row or "'sun'" in (row["sql"] or ""):
        return
    connection.execute("ALTER TABLE teacher_work_schedule RENAME TO teacher_work_schedule_legacy")
    connection.execute(
        """
        CREATE TABLE teacher_work_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            academy_teacher_id TEXT NOT NULL REFERENCES academy_teachers(id) ON DELETE CASCADE,
            day TEXT NOT NULL CHECK(day IN ('mon','tue','wed','thu','fri','sat','sun')),
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            break_minutes INTEGER NOT NULL DEFAULT 0,
            note TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            UNIQUE(academy_teacher_id, day)
        )
        """
    )
    connection.execute(
        """
        INSERT INTO teacher_work_schedule(
          id,academy_teacher_id,day,start_time,end_time,break_minutes,note,updated_at
        )
        SELECT id,academy_teacher_id,day,start_time,end_time,break_minutes,note,updated_at
        FROM teacher_work_schedule_legacy
        """
    )
    connection.execute("DROP TABLE teacher_work_schedule_legacy")


def ensure_schedule_change_adjustments(connection: sqlite3.Connection) -> None:
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='attendance_adjustment_requests'"
    ).fetchone()
    table_sql = (row["sql"] or "") if row else ""
    if not row or ("'schedule_change'" in table_sql and "'absence'" in table_sql):
        return
    connection.execute(
        "ALTER TABLE attendance_adjustment_requests RENAME TO attendance_adjustment_requests_legacy"
    )
    connection.execute(
        """
        CREATE TABLE attendance_adjustment_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT NOT NULL REFERENCES teachers(id),
            request_type TEXT NOT NULL CHECK(request_type IN ('early_leave','overtime','schedule_change','absence')),
            work_date TEXT NOT NULL,
            start_time TEXT NOT NULL DEFAULT '',
            end_time TEXT NOT NULL,
            reason TEXT NOT NULL,
            requested_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
            reviewed_at TEXT,
            review_note TEXT
        )
        """
    )
    connection.execute(
        """
        INSERT INTO attendance_adjustment_requests(
          id,teacher_id,request_type,work_date,start_time,end_time,reason,
          requested_at,status,reviewed_at,review_note
        )
        SELECT id,teacher_id,request_type,work_date,start_time,end_time,reason,
               requested_at,status,reviewed_at,review_note
        FROM attendance_adjustment_requests_legacy
        """
    )
    connection.execute("DROP TABLE attendance_adjustment_requests_legacy")
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_adjustment_teacher_date ON attendance_adjustment_requests(teacher_id, work_date, requested_at)"
    )


def init_db() -> None:
    with db() as connection:
        connection.executescript(
            """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS teachers (
                id TEXT PRIMARY KEY,
                kakao_id TEXT UNIQUE,
                name TEXT NOT NULL,
                profile_image TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                teacher_id TEXT NOT NULL REFERENCES teachers(id),
                expires_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS owner_accounts (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                iterations INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS owner_sessions (
                token_hash TEXT PRIMARY KEY,
                username TEXT NOT NULL REFERENCES owner_accounts(username) ON DELETE CASCADE,
                expires_at INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS attendance_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id TEXT NOT NULL REFERENCES teachers(id),
                event_type TEXT NOT NULL CHECK(event_type IN ('clock_in', 'clock_out')),
                work_date TEXT NOT NULL,
                requested_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
                reviewed_at TEXT,
                review_note TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_attendance_teacher_date
              ON attendance_requests(teacher_id, work_date, requested_at);
            CREATE TABLE IF NOT EXISTS teacher_work_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                academy_teacher_id TEXT NOT NULL REFERENCES academy_teachers(id) ON DELETE CASCADE,
                day TEXT NOT NULL CHECK(day IN ('mon','tue','wed','thu','fri','sat','sun')),
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                break_minutes INTEGER NOT NULL DEFAULT 0,
                note TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL,
                UNIQUE(academy_teacher_id, day)
            );
            CREATE TABLE IF NOT EXISTS attendance_adjustment_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id TEXT NOT NULL REFERENCES teachers(id),
                request_type TEXT NOT NULL CHECK(request_type IN ('early_leave','overtime','schedule_change','absence')),
                work_date TEXT NOT NULL,
                start_time TEXT NOT NULL DEFAULT '',
                end_time TEXT NOT NULL,
                reason TEXT NOT NULL,
                requested_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
                reviewed_at TEXT,
                review_note TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_adjustment_teacher_date
              ON attendance_adjustment_requests(teacher_id, work_date, requested_at);
            CREATE TABLE IF NOT EXISTS class_schedule (
                id TEXT PRIMARY KEY,
                day TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                time_label TEXT,
                class_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                teacher_name TEXT NOT NULL,
                students_json TEXT NOT NULL DEFAULT '[]',
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_class_schedule_teacher_day
              ON class_schedule(teacher_name, day, start_time);
            CREATE TABLE IF NOT EXISTS academy_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS academy_teachers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                subject TEXT NOT NULL DEFAULT '',
                sort_order INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS academy_classes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                level TEXT NOT NULL DEFAULT '',
                teacher_id TEXT REFERENCES academy_teachers(id),
                sort_order INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS academy_teacher_classes (
                teacher_id TEXT NOT NULL REFERENCES academy_teachers(id) ON DELETE CASCADE,
                class_id TEXT NOT NULL REFERENCES academy_classes(id) ON DELETE CASCADE,
                PRIMARY KEY (teacher_id, class_id)
            );
            CREATE TABLE IF NOT EXISTS academy_students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                school TEXT NOT NULL DEFAULT '',
                class_id TEXT REFERENCES academy_classes(id),
                parent_name TEXT NOT NULL DEFAULT '',
                latest_progress TEXT NOT NULL DEFAULT '',
                focus TEXT NOT NULL DEFAULT '',
                sort_order INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS lesson_records (
                id TEXT PRIMARY KEY,
                lesson_date TEXT NOT NULL,
                class_id TEXT REFERENCES academy_classes(id),
                teacher_id TEXT REFERENCES academy_teachers(id),
                student_id TEXT NOT NULL REFERENCES academy_students(id),
                progress_code TEXT NOT NULL DEFAULT '',
                title TEXT NOT NULL,
                summary TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS lesson_record_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT NOT NULL REFERENCES lesson_records(id) ON DELETE CASCADE,
                original_name TEXT NOT NULL,
                stored_name TEXT,
                mime_type TEXT,
                size_bytes INTEGER,
                sort_order INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS dashboard_schedule (
                id TEXT PRIMARY KEY,
                time_label TEXT NOT NULL DEFAULT '',
                class_id TEXT REFERENCES academy_classes(id),
                progress_code TEXT NOT NULL DEFAULT '',
                topic TEXT NOT NULL DEFAULT '',
                record_status TEXT NOT NULL DEFAULT '',
                photo_count INTEGER NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS weekly_feedback (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL REFERENCES academy_students(id),
                lesson_count INTEGER NOT NULL DEFAULT 0,
                photo_count INTEGER NOT NULL DEFAULT 0,
                summary TEXT NOT NULL DEFAULT '',
                individual_feedback TEXT NOT NULL DEFAULT '',
                next_plan TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT '',
                sort_order INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS consultations (
                id TEXT PRIMARY KEY,
                consultation_date TEXT NOT NULL,
                student_id TEXT NOT NULL REFERENCES academy_students(id),
                consultation_type TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL,
                followup_date TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS student_evaluations (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                lesson_date TEXT NOT NULL,
                teacher_id TEXT NOT NULL,
                academy_teacher_id TEXT NOT NULL DEFAULT '',
                teacher_name TEXT NOT NULL,
                student_id TEXT NOT NULL,
                student_name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                subject TEXT NOT NULL DEFAULT '',
                attitude INTEGER NOT NULL CHECK(attitude BETWEEN 1 AND 4),
                concentration INTEGER NOT NULL CHECK(concentration BETWEEN 1 AND 4),
                understanding INTEGER NOT NULL CHECK(understanding BETWEEN 1 AND 4),
                progress INTEGER NOT NULL CHECK(progress BETWEEN 1 AND 4),
                participation INTEGER NOT NULL CHECK(participation BETWEEN 1 AND 4),
                homework INTEGER NOT NULL CHECK(homework BETWEEN 1 AND 4),
                note TEXT NOT NULL,
                message_draft TEXT NOT NULL DEFAULT '',
                message_status TEXT NOT NULL DEFAULT 'pending'
                  CHECK(message_status IN ('pending','draft','sent','updated_after_sent')),
                message_provider TEXT NOT NULL DEFAULT '',
                message_updated_at TEXT,
                sent_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(lesson_id, lesson_date, student_id)
            );
            CREATE TABLE IF NOT EXISTS student_attendance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id TEXT NOT NULL,
                lesson_date TEXT NOT NULL,
                teacher_id TEXT NOT NULL,
                academy_teacher_id TEXT NOT NULL DEFAULT '',
                teacher_name TEXT NOT NULL,
                student_id TEXT NOT NULL,
                student_name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                subject TEXT NOT NULL DEFAULT '',
                attendance_status TEXT NOT NULL
                  CHECK(attendance_status IN ('present','late','absent','excused','makeup')),
                note TEXT NOT NULL DEFAULT '',
                recorded_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(lesson_id, lesson_date, student_id)
            );
            CREATE TABLE IF NOT EXISTS teacher_employment_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                academy_teacher_id TEXT NOT NULL,
                event_type TEXT NOT NULL
                  CHECK(event_type IN ('hire','termination','rehire','status_change')),
                effective_date TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                recorded_at TEXT NOT NULL,
                UNIQUE(academy_teacher_id, event_type, effective_date)
            );
            CREATE TABLE IF NOT EXISTS student_status_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                status TEXT NOT NULL,
                effective_date TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                UNIQUE(student_id, status, effective_date)
            );
            CREATE TABLE IF NOT EXISTS kakao_parent_rooms (
                student_id TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                room_title TEXT NOT NULL,
                linked_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS kakao_send_log (
                id TEXT PRIMARY KEY,
                evaluation_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                chat_id TEXT NOT NULL,
                room_title TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('sending','sent','unknown')),
                attempted_at TEXT NOT NULL,
                finished_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_student_evaluations_date
              ON student_evaluations(lesson_date, updated_at);
            CREATE INDEX IF NOT EXISTS idx_student_evaluations_student
              ON student_evaluations(student_id, lesson_date);
            CREATE INDEX IF NOT EXISTS idx_student_attendance_student_date
              ON student_attendance_records(student_id, lesson_date);
            CREATE INDEX IF NOT EXISTS idx_student_attendance_teacher_date
              ON student_attendance_records(teacher_id, lesson_date);
            CREATE INDEX IF NOT EXISTS idx_teacher_employment_events
              ON teacher_employment_events(academy_teacher_id, effective_date);
            CREATE INDEX IF NOT EXISTS idx_student_status_events
              ON student_status_events(student_id, effective_date);
            CREATE INDEX IF NOT EXISTS idx_kakao_send_log_evaluation
              ON kakao_send_log(evaluation_id, attempted_at);
            CREATE TABLE IF NOT EXISTS kiosk_pairing_codes (
                code_hash TEXT PRIMARY KEY,
                expires_at INTEGER NOT NULL,
                used_at TEXT
            );
            CREATE TABLE IF NOT EXISTS kiosk_devices (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                token_hash TEXT UNIQUE NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS student_checkins (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                student_name TEXT NOT NULL,
                checkin_date TEXT NOT NULL,
                checked_in_at TEXT NOT NULL,
                device_id TEXT NOT NULL,
                notification_status TEXT NOT NULL DEFAULT 'pending',
                notification_message TEXT NOT NULL DEFAULT '',
                notification_finished_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_student_checkins_date
              ON student_checkins(checkin_date, checked_in_at);
            CREATE INDEX IF NOT EXISTS idx_student_checkins_student
              ON student_checkins(student_id, checked_in_at);
            """
        )
        ensure_sunday_work_schedule(connection)
        ensure_schedule_change_adjustments(connection)
        ensure_column(connection, "teachers", "academy_teacher_id", "TEXT")
        ensure_column(connection, "class_schedule", "teacher_id", "TEXT")
        ensure_column(connection, "class_schedule", "student_ids_json", "TEXT NOT NULL DEFAULT '[]'")
        ensure_column(connection, "academy_teachers", "phone", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "email", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "address", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "university", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "major", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "career", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "certifications", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "hire_date", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "termination_date", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "employment_type", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "salary_type", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "salary_amount", "INTEGER NOT NULL DEFAULT 0")
        ensure_column(connection, "academy_teachers", "notes", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_teachers", "active", "INTEGER NOT NULL DEFAULT 1")
        ensure_column(connection, "academy_students", "phone", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_students", "grade", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_students", "guardian_phone", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_students", "address", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_students", "birth_date", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_students", "enrollment_date", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_students", "status", "TEXT NOT NULL DEFAULT '재원'")
        ensure_column(connection, "academy_students", "notes", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "academy_students", "checkin_code", "TEXT NOT NULL DEFAULT ''")
        for row in connection.execute(
            "SELECT id,hire_date,termination_date,active FROM academy_teachers"
        ):
            if row["hire_date"]:
                connection.execute(
                    "INSERT OR IGNORE INTO teacher_employment_events(academy_teacher_id,event_type,effective_date,note,recorded_at) VALUES (?,?,?,?,?)",
                    (row["id"], "hire", row["hire_date"], "입사일 등록", iso_now()),
                )
            if row["termination_date"]:
                connection.execute(
                    "INSERT OR IGNORE INTO teacher_employment_events(academy_teacher_id,event_type,effective_date,note,recorded_at) VALUES (?,?,?,?,?)",
                    (row["id"], "termination", row["termination_date"], "퇴사일 등록", iso_now()),
                )
        for row in connection.execute(
            "SELECT id,status,enrollment_date FROM academy_students"
        ):
            effective_date = row["enrollment_date"] or now_kst().date().isoformat()
            connection.execute(
                "INSERT OR IGNORE INTO student_status_events(student_id,status,effective_date,recorded_at) VALUES (?,?,?,?)",
                (row["id"], row["status"] or "재원", effective_date, iso_now()),
            )
        connection.execute(
            """
            INSERT OR IGNORE INTO student_attendance_records(
              lesson_id,lesson_date,teacher_id,academy_teacher_id,teacher_name,
              student_id,student_name,class_name,subject,attendance_status,note,
              recorded_at,updated_at
            )
            SELECT lesson_id,lesson_date,teacher_id,academy_teacher_id,teacher_name,
                   student_id,student_name,class_name,subject,'present','',created_at,updated_at
            FROM student_evaluations
            """
        )
        for teacher_id, name in (("demo1", "이선생"), ("demo2", "최선생")):
            connection.execute(
                "INSERT OR IGNORE INTO teachers(id, kakao_id, name, created_at) VALUES (?, NULL, ?, ?)",
                (teacher_id, name, iso_now()),
            )
        connection.execute("UPDATE teachers SET academy_teacher_id='t1' WHERE id='demo1' AND academy_teacher_id IS NULL")
        connection.execute("UPDATE teachers SET academy_teacher_id='t2' WHERE id='demo2' AND academy_teacher_id IS NULL")


def owner_state_initialized(connection: sqlite3.Connection) -> bool:
    row = connection.execute(
        "SELECT value FROM academy_meta WHERE key='owner_state_initialized'"
    ).fetchone()
    return bool(row and row["value"] == "1")


def json_list(value: str | None) -> list:
    try:
        parsed = json.loads(value or "[]")
        return parsed if isinstance(parsed, list) else []
    except (TypeError, json.JSONDecodeError):
        return []


def normalize_phone(value: str | None) -> str:
    digits = "".join(character for character in str(value or "") if character.isdigit())
    if digits.startswith("0082"):
        digits = digits[2:]
    if digits.startswith("82"):
        digits = f"0{digits[2:]}"
    return digits


def time_minutes(value: str) -> int:
    try:
        hour_text, minute_text = value.split(":", 1)
        hour, minute = int(hour_text), int(minute_text)
    except (AttributeError, TypeError, ValueError) as error:
        raise ValueError("시간은 HH:MM 형식으로 입력해 주세요.") from error
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("시간 범위가 올바르지 않습니다.")
    return hour * 60 + minute


def day_key_for_date(value: str) -> str:
    try:
        return DAY_KEYS[datetime.strptime(value, "%Y-%m-%d").weekday()]
    except (TypeError, ValueError) as error:
        raise ValueError("근무일 형식이 올바르지 않습니다.") from error


def replace_teacher_work_schedule(
    connection: sqlite3.Connection, academy_teacher_id: str, schedule: list[dict]
) -> None:
    teacher = connection.execute(
        "SELECT id FROM academy_teachers WHERE id=? AND active=1", (academy_teacher_id,)
    ).fetchone()
    if not teacher:
        raise ValueError("재직 중인 선생님을 찾을 수 없습니다.")
    if not isinstance(schedule, list) or len(schedule) > 7:
        raise ValueError("주간 근무시간 형식이 올바르지 않습니다.")
    cleaned = []
    seen_days = set()
    for item in schedule:
        if not isinstance(item, dict):
            raise ValueError("근무시간 항목 형식이 올바르지 않습니다.")
        day = text_value(item, "day", 10)
        start_time = text_value(item, "startTime", 5)
        end_time = text_value(item, "endTime", 5)
        if day not in SCHEDULE_DAYS or day in seen_days:
            raise ValueError("근무 요일이 올바르지 않거나 중복되었습니다.")
        start_minutes = time_minutes(start_time)
        end_minutes = time_minutes(end_time)
        if end_minutes <= start_minutes:
            raise ValueError("퇴근 예정 시간은 출근 예정 시간보다 늦어야 합니다.")
        try:
            break_minutes = max(0, int(item.get("breakMinutes", 0) or 0))
        except (TypeError, ValueError) as error:
            raise ValueError("휴게시간은 분 단위 숫자로 입력해 주세요.") from error
        if break_minutes >= end_minutes - start_minutes or break_minutes > 480:
            raise ValueError("휴게시간이 전체 근무시간보다 짧은지 확인해 주세요.")
        seen_days.add(day)
        cleaned.append((
            academy_teacher_id, day, start_time, end_time, break_minutes,
            text_value(item, "note", 500), iso_now(),
        ))
    connection.execute(
        "DELETE FROM teacher_work_schedule WHERE academy_teacher_id=?", (academy_teacher_id,)
    )
    connection.executemany(
        """
        INSERT INTO teacher_work_schedule(
          academy_teacher_id,day,start_time,end_time,break_minutes,note,updated_at
        ) VALUES (?,?,?,?,?,?,?)
        """,
        cleaned,
    )


def record_teacher_absence(
    connection: sqlite3.Connection, academy_teacher_id: str, work_date: str, reason: str
) -> int:
    """원장이 확정한 결근을 승인 완료 기록으로 바로 누적한다."""
    teacher_profile = connection.execute(
        "SELECT id,name FROM academy_teachers WHERE id=?", (academy_teacher_id,)
    ).fetchone()
    if not teacher_profile:
        raise ValueError("선생님을 찾을 수 없습니다.")
    try:
        parsed_date = datetime.strptime(work_date, "%Y-%m-%d").date()
    except (TypeError, ValueError) as error:
        raise ValueError("결근일을 올바르게 선택해 주세요.") from error
    if parsed_date > now_kst().date():
        raise ValueError("아직 지나지 않은 날짜는 결근으로 확정할 수 없습니다.")
    reason = str(reason or "").strip()[:1000]
    if len(reason) < 2:
        raise ValueError("결근 사유를 입력해 주세요.")
    plan = connection.execute(
        "SELECT id FROM teacher_work_schedule WHERE academy_teacher_id=? AND day=?",
        (academy_teacher_id, day_key_for_date(work_date)),
    ).fetchone()
    if not plan:
        raise ValueError("선택한 날짜에 등록된 예정 근무가 없습니다.")
    teacher_login = connection.execute(
        """
        SELECT id FROM teachers WHERE academy_teacher_id=?
        ORDER BY CASE WHEN kakao_id IS NOT NULL THEN 0 ELSE 1 END, created_at LIMIT 1
        """,
        (academy_teacher_id,),
    ).fetchone()
    if not teacher_login:
        raise ValueError("선생님 앱 계정 연결 정보를 찾을 수 없습니다.")
    worked = connection.execute(
        """
        SELECT id FROM attendance_requests
        WHERE teacher_id=? AND work_date=? AND event_type='clock_in' AND status='approved'
        """,
        (teacher_login["id"], work_date),
    ).fetchone()
    if worked:
        raise ValueError("이미 승인된 출근 기록이 있어 결근으로 처리할 수 없습니다.")
    duplicate = connection.execute(
        """
        SELECT id FROM attendance_adjustment_requests
        WHERE teacher_id=? AND work_date=? AND request_type='absence'
          AND status IN ('pending','approved')
        """,
        (teacher_login["id"], work_date),
    ).fetchone()
    if duplicate:
        raise ValueError("해당 날짜의 결근 기록이 이미 있습니다.")
    timestamp = iso_now()
    cursor = connection.execute(
        """
        INSERT INTO attendance_adjustment_requests(
          teacher_id,request_type,work_date,start_time,end_time,reason,requested_at,
          status,reviewed_at,review_note
        ) VALUES (?,'absence',?,'','',?,?, 'approved',?,'원장 직접 기록')
        """,
        (teacher_login["id"], work_date, reason, timestamp, timestamp),
    )
    return int(cursor.lastrowid)


def serialize_owner_state(connection: sqlite3.Connection) -> dict:
    teachers = [
        {
            "id": row["id"],
            "name": row["name"],
            "subject": row["subject"],
            "phone": row["phone"],
            "email": row["email"],
            "address": row["address"],
            "university": row["university"],
            "major": row["major"],
            "career": row["career"],
            "certifications": row["certifications"],
            "hireDate": row["hire_date"],
            "terminationDate": row["termination_date"],
            "employmentType": row["employment_type"],
            "salaryType": row["salary_type"],
            "salaryAmount": row["salary_amount"],
            "notes": row["notes"],
            "active": bool(row["active"]),
            "classes": [
                item["class_id"]
                for item in connection.execute(
                    "SELECT class_id FROM academy_teacher_classes WHERE teacher_id=? ORDER BY class_id",
                    (row["id"],),
                )
            ],
        }
        for row in connection.execute("SELECT * FROM academy_teachers ORDER BY sort_order, id")
    ]
    students = [
        {
            "id": row["id"],
            "name": row["name"],
            "school": row["school"],
            "phone": row["phone"],
            "grade": row["grade"],
            "classId": row["class_id"] or "",
            "parent": row["parent_name"],
            "guardianPhone": row["guardian_phone"],
            "checkinCode": row["checkin_code"],
            "address": row["address"],
            "birthDate": row["birth_date"],
            "enrollmentDate": row["enrollment_date"],
            "status": row["status"],
            "notes": row["notes"],
            "latest": row["latest_progress"],
            "focus": row["focus"],
        }
        for row in connection.execute("SELECT * FROM academy_students ORDER BY sort_order, id")
    ]
    student_ids_by_class: dict[str, list[str]] = {}
    for student in students:
        student_ids_by_class.setdefault(student["classId"], []).append(student["id"])
    classes = [
        {
            "id": row["id"],
            "name": row["name"],
            "level": row["level"],
            "teacherId": row["teacher_id"] or "",
            "students": student_ids_by_class.get(row["id"], []),
        }
        for row in connection.execute("SELECT * FROM academy_classes ORDER BY sort_order, id")
    ]
    records = []
    for row in connection.execute("SELECT * FROM lesson_records ORDER BY sort_order, id"):
        photos = [
            {
                "originalName": photo["original_name"],
                "storedName": photo["stored_name"] or "",
                "mimeType": photo["mime_type"] or "",
                "size": photo["size_bytes"] or 0,
                "url": f"/media/{urllib.parse.quote(photo['stored_name'])}" if photo["stored_name"] else "",
            }
            for photo in connection.execute(
                """
                SELECT original_name, stored_name, mime_type, size_bytes
                FROM lesson_record_photos WHERE record_id=? ORDER BY sort_order, id
                """,
                (row["id"],),
            )
        ]
        records.append({
            "id": row["id"],
            "date": row["lesson_date"],
            "classId": row["class_id"] or "",
            "teacherId": row["teacher_id"] or "",
            "studentId": row["student_id"],
            "code": row["progress_code"],
            "title": row["title"],
            "summary": row["summary"],
            "notes": row["notes"],
            "photos": photos,
            "status": row["status"],
        })
    schedule = [
        {
            "time": row["time_label"],
            "classId": row["class_id"] or "",
            "code": row["progress_code"],
            "topic": row["topic"],
            "recordStatus": row["record_status"],
            "photos": row["photo_count"],
        }
        for row in connection.execute("SELECT * FROM dashboard_schedule ORDER BY sort_order, id")
    ]
    feedback = [
        {
            "id": row["id"],
            "studentId": row["student_id"],
            "lessons": row["lesson_count"],
            "photos": row["photo_count"],
            "summary": row["summary"],
            "individual": row["individual_feedback"],
            "next": row["next_plan"],
            "status": row["status"],
        }
        for row in connection.execute("SELECT * FROM weekly_feedback ORDER BY sort_order, id")
    ]
    weekly_schedule = []
    for row in connection.execute(
        """
        SELECT id, day, start_time, end_time, time_label, class_name, subject,
               teacher_name, teacher_id, students_json, student_ids_json
        FROM class_schedule
        ORDER BY CASE day
          WHEN 'mon' THEN 1 WHEN 'tue' THEN 2 WHEN 'wed' THEN 3
          WHEN 'thu' THEN 4 WHEN 'fri' THEN 5 WHEN 'sat' THEN 6 ELSE 7 END,
          start_time, id
        """
    ):
        student_ids = json_list(row["student_ids_json"])
        if not student_ids:
            student_ids = [item.get("id") for item in json_list(row["students_json"]) if item.get("id")]
        weekly_schedule.append({
            "id": row["id"],
            "day": row["day"],
            "start": row["start_time"],
            "end": row["end_time"] or "",
            "timeLabel": row["time_label"] or "",
            "className": row["class_name"],
            "subject": row["subject"],
            "teacherId": row["teacher_id"] or "",
            "studentIds": student_ids,
        })
    consultations = [
        {
            "id": row["id"],
            "date": row["consultation_date"],
            "studentId": row["student_id"],
            "type": row["consultation_type"],
            "summary": row["summary"],
            "followup": row["followup_date"],
        }
        for row in connection.execute("SELECT * FROM consultations ORDER BY sort_order, id")
    ]
    attendance_summary: dict[str, dict] = {}
    for row in connection.execute(
        """
        SELECT student_id,attendance_status,COUNT(*) AS count
        FROM student_attendance_records
        GROUP BY student_id,attendance_status
        """
    ):
        item = attendance_summary.setdefault(row["student_id"], {
            "studentId": row["student_id"], "total": 0,
            "present": 0, "late": 0, "absent": 0, "excused": 0, "makeup": 0,
        })
        item[row["attendance_status"]] = row["count"]
        item["total"] += row["count"]
    return {
        "classes": classes,
        "teachers": teachers,
        "students": students,
        "records": records,
        "schedule": schedule,
        "weeklyFeedback": feedback,
        "weeklySchedule": weekly_schedule,
        "attendance": [],
        "studentAttendanceSummary": list(attendance_summary.values()),
        "consultations": consultations,
    }


def text_value(item: dict, key: str, limit: int, default: str = "") -> str:
    return str(item.get(key, default) or default).strip()[:limit]


def nonnegative_int(item: dict, key: str) -> int:
    try:
        return max(0, int(item.get(key, 0) or 0))
    except (TypeError, ValueError) as error:
        raise ValueError(f"{key} 값은 0 이상의 숫자여야 합니다.") from error


def required_id(item: dict, key: str, label: str) -> str:
    value = text_value(item, key, 80)
    if not value:
        raise ValueError(f"{label} ID가 필요합니다.")
    return value


def state_list(state: dict, key: str, limit: int) -> list[dict]:
    value = state.get(key, [])
    if not isinstance(value, list) or len(value) > limit or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"{key} 데이터 형식이 올바르지 않습니다.")
    return value


def replace_owner_state(connection: sqlite3.Connection, state: dict) -> None:
    if not isinstance(state, dict):
        raise ValueError("운영 데이터 형식이 올바르지 않습니다.")
    teachers = state_list(state, "teachers", 300)
    classes = state_list(state, "classes", 500)
    students = state_list(state, "students", 10000)
    records = state_list(state, "records", 20000)
    schedule = state_list(state, "schedule", 1000)
    feedback = state_list(state, "weeklyFeedback", 10000)
    weekly_schedule = state_list(state, "weeklySchedule", 1000)
    consultations = state_list(state, "consultations", 20000)

    previous_teachers = {
        row["id"]: dict(row)
        for row in connection.execute(
            "SELECT id,hire_date,termination_date,active FROM academy_teachers"
        )
    }
    previous_students = {
        row["id"]: dict(row)
        for row in connection.execute(
            "SELECT id,status,enrollment_date FROM academy_students"
        )
    }

    teacher_ids = {required_id(item, "id", "선생님") for item in teachers}
    class_ids = {required_id(item, "id", "반") for item in classes}
    student_ids = {required_id(item, "id", "학생") for item in students}
    if len(teacher_ids) != len(teachers) or len(class_ids) != len(classes) or len(student_ids) != len(students):
        raise ValueError("선생님·반·학생 ID가 중복되었습니다.")
    preserved_work_schedules = [
        dict(row)
        for row in connection.execute(
            """
            SELECT academy_teacher_id,day,start_time,end_time,break_minutes,note,updated_at
            FROM teacher_work_schedule
            """
        )
        if row["academy_teacher_id"] in teacher_ids
    ]

    connection.execute("DELETE FROM lesson_record_photos")
    connection.execute("DELETE FROM lesson_records")
    connection.execute("DELETE FROM weekly_feedback")
    connection.execute("DELETE FROM consultations")
    connection.execute("DELETE FROM dashboard_schedule")
    connection.execute("DELETE FROM academy_teacher_classes")
    connection.execute("DELETE FROM academy_students")
    connection.execute("DELETE FROM academy_classes")
    connection.execute("DELETE FROM academy_teachers")

    for index, item in enumerate(teachers):
        teacher_id = required_id(item, "id", "선생님")
        name = text_value(item, "name", 100)
        if not name:
            raise ValueError("선생님 이름이 필요합니다.")
        connection.execute(
            """
            INSERT INTO academy_teachers(
              id,name,subject,phone,email,address,university,major,career,certifications,
              hire_date,termination_date,employment_type,salary_type,salary_amount,notes,active,sort_order
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                teacher_id, name, text_value(item, "subject", 200),
                text_value(item, "phone", 40), text_value(item, "email", 200),
                text_value(item, "address", 500), text_value(item, "university", 200),
                text_value(item, "major", 200), text_value(item, "career", 5000),
                text_value(item, "certifications", 2000), text_value(item, "hireDate", 10),
                text_value(item, "terminationDate", 10),
                text_value(item, "employmentType", 80), text_value(item, "salaryType", 80),
                nonnegative_int(item, "salaryAmount"), text_value(item, "notes", 5000),
                1 if item.get("active", True) else 0, index,
            ),
        )
        previous = previous_teachers.get(teacher_id)
        hire_date = text_value(item, "hireDate", 10)
        termination_date = text_value(item, "terminationDate", 10)
        is_active = bool(item.get("active", True))
        if hire_date:
            connection.execute(
                "INSERT OR IGNORE INTO teacher_employment_events(academy_teacher_id,event_type,effective_date,note,recorded_at) VALUES (?,?,?,?,?)",
                (teacher_id, "hire", hire_date, "입사일 등록", iso_now()),
            )
        if termination_date:
            connection.execute(
                "INSERT OR IGNORE INTO teacher_employment_events(academy_teacher_id,event_type,effective_date,note,recorded_at) VALUES (?,?,?,?,?)",
                (teacher_id, "termination", termination_date, "퇴사일 등록", iso_now()),
            )
        if previous and bool(previous["active"]) != is_active:
            event_type = "rehire" if is_active else "termination"
            effective_date = hire_date if is_active else termination_date
            effective_date = effective_date or now_kst().date().isoformat()
            note = "재직 상태로 변경" if is_active else "퇴직 상태로 변경"
            connection.execute(
                "INSERT OR IGNORE INTO teacher_employment_events(academy_teacher_id,event_type,effective_date,note,recorded_at) VALUES (?,?,?,?,?)",
                (teacher_id, event_type, effective_date, note, iso_now()),
            )
        login_teacher = connection.execute(
            """
            SELECT id FROM teachers
            WHERE academy_teacher_id=? OR (name=? AND kakao_id IS NULL)
            ORDER BY CASE WHEN academy_teacher_id=? THEN 0 ELSE 1 END, created_at
            LIMIT 1
            """,
            (teacher_id, name, teacher_id),
        ).fetchone()
        if login_teacher:
            connection.execute(
                "UPDATE teachers SET name=?, academy_teacher_id=?, active=? WHERE id=?",
                (name, teacher_id, 1 if item.get("active", True) else 0, login_teacher["id"]),
            )
        else:
            login_id = f"staff:{teacher_id}"
            connection.execute(
                """
                INSERT OR IGNORE INTO teachers(id,kakao_id,name,active,created_at,academy_teacher_id)
                VALUES (?,NULL,?,?,?,?)
                """,
                (login_id, name, 1 if item.get("active", True) else 0, iso_now(), teacher_id),
            )
    connection.executemany(
        """
        INSERT INTO teacher_work_schedule(
          academy_teacher_id,day,start_time,end_time,break_minutes,note,updated_at
        ) VALUES (?,?,?,?,?,?,?)
        """,
        [
            (
                item["academy_teacher_id"], item["day"], item["start_time"], item["end_time"],
                item["break_minutes"], item["note"], item["updated_at"],
            )
            for item in preserved_work_schedules
        ],
    )
    for index, item in enumerate(classes):
        class_id = required_id(item, "id", "반")
        name = text_value(item, "name", 120)
        teacher_id = text_value(item, "teacherId", 80) or None
        if not name or (teacher_id and teacher_id not in teacher_ids):
            raise ValueError("반 이름 또는 담당 선생님 정보가 올바르지 않습니다.")
        connection.execute(
            "INSERT INTO academy_classes(id,name,level,teacher_id,sort_order) VALUES (?,?,?,?,?)",
            (class_id, name, text_value(item, "level", 120), teacher_id, index),
        )
    for item in teachers:
        teacher_id = required_id(item, "id", "선생님")
        linked_classes = item.get("classes") or []
        if not isinstance(linked_classes, list):
            raise ValueError("선생님 반 배정 형식이 올바르지 않습니다.")
        for class_id in linked_classes:
            if class_id in class_ids:
                connection.execute(
                    "INSERT OR IGNORE INTO academy_teacher_classes(teacher_id,class_id) VALUES (?,?)",
                    (teacher_id, class_id),
                )
    for item in classes:
        teacher_id = text_value(item, "teacherId", 80)
        if teacher_id:
            connection.execute(
                "INSERT OR IGNORE INTO academy_teacher_classes(teacher_id,class_id) VALUES (?,?)",
                (teacher_id, required_id(item, "id", "반")),
            )
    for index, item in enumerate(students):
        student_id = required_id(item, "id", "학생")
        name = text_value(item, "name", 100)
        class_id = text_value(item, "classId", 80) or None
        if not name or (class_id and class_id not in class_ids):
            raise ValueError("학생 이름 또는 반 정보가 올바르지 않습니다.")
        connection.execute(
            """
            INSERT INTO academy_students(
              id,name,school,phone,grade,class_id,parent_name,guardian_phone,address,
              birth_date,enrollment_date,status,notes,latest_progress,focus,checkin_code,sort_order
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                student_id, name, text_value(item, "school", 160),
                text_value(item, "phone", 40), text_value(item, "grade", 80), class_id,
                text_value(item, "parent", 120), text_value(item, "guardianPhone", 40),
                text_value(item, "address", 500), text_value(item, "birthDate", 10),
                text_value(item, "enrollmentDate", 10), text_value(item, "status", 40, "재원"),
                text_value(item, "notes", 5000), text_value(item, "latest", 80),
                text_value(item, "focus", 2000), text_value(item, "checkinCode", 8), index,
            ),
        )
        previous = previous_students.get(student_id)
        status = text_value(item, "status", 40, "재원")
        if not previous or previous["status"] != status:
            effective_date = text_value(item, "enrollmentDate", 10) if not previous else now_kst().date().isoformat()
            connection.execute(
                "INSERT OR IGNORE INTO student_status_events(student_id,status,effective_date,recorded_at) VALUES (?,?,?,?)",
                (student_id, status, effective_date or now_kst().date().isoformat(), iso_now()),
            )
    for index, item in enumerate(records):
        record_id = required_id(item, "id", "수업기록")
        student_id = text_value(item, "studentId", 80)
        class_id = text_value(item, "classId", 80) or None
        teacher_id = text_value(item, "teacherId", 80) or None
        if student_id not in student_ids or (class_id and class_id not in class_ids) or (teacher_id and teacher_id not in teacher_ids):
            raise ValueError("수업기록의 학생·반·선생님 연결 정보가 올바르지 않습니다.")
        connection.execute(
            """
            INSERT INTO lesson_records(
              id,lesson_date,class_id,teacher_id,student_id,progress_code,title,
              summary,notes,status,created_at,sort_order
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                record_id, text_value(item, "date", 10), class_id, teacher_id, student_id,
                text_value(item, "code", 80), text_value(item, "title", 300),
                text_value(item, "summary", 10000), text_value(item, "notes", 10000),
                text_value(item, "status", 80), iso_now(), index,
            ),
        )
        photos = item.get("photos") or []
        if not isinstance(photos, list) or len(photos) > 100:
            raise ValueError("수업 사진 목록 형식이 올바르지 않습니다.")
        for photo_index, photo_name in enumerate(photos):
            if isinstance(photo_name, dict):
                original_name = text_value(photo_name, "originalName", 255)
                stored_name = text_value(photo_name, "storedName", 100) or None
                mime_type = text_value(photo_name, "mimeType", 100) or None
                size_bytes = max(0, int(photo_name.get("size", 0) or 0))
            else:
                original_name = str(photo_name)[:255]
                stored_name = None
                mime_type = None
                size_bytes = 0
            if stored_name and (Path(stored_name).name != stored_name or not (PHOTO_PATH / stored_name).is_file()):
                raise ValueError("저장된 수업 사진 파일을 찾을 수 없습니다.")
            connection.execute(
                """
                INSERT INTO lesson_record_photos(
                  record_id,original_name,stored_name,mime_type,size_bytes,sort_order
                ) VALUES (?,?,?,?,?,?)
                """,
                (record_id, original_name, stored_name, mime_type, size_bytes, photo_index),
            )
    for index, item in enumerate(schedule):
        class_id = text_value(item, "classId", 80) or None
        if class_id and class_id not in class_ids:
            raise ValueError("오늘 수업 일정의 반 정보가 올바르지 않습니다.")
        connection.execute(
            """
            INSERT INTO dashboard_schedule(
              id,time_label,class_id,progress_code,topic,record_status,photo_count,sort_order
            ) VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                f"dashboard-{index}", text_value(item, "time", 40), class_id,
                text_value(item, "code", 80), text_value(item, "topic", 300),
                text_value(item, "recordStatus", 80), max(0, int(item.get("photos", 0) or 0)), index,
            ),
        )
    for index, item in enumerate(feedback):
        student_id = text_value(item, "studentId", 80)
        if student_id not in student_ids:
            raise ValueError("주간 피드백의 학생 정보가 올바르지 않습니다.")
        connection.execute(
            """
            INSERT INTO weekly_feedback(
              id,student_id,lesson_count,photo_count,summary,individual_feedback,next_plan,status,sort_order
            ) VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                required_id(item, "id", "주간 피드백"), student_id,
                max(0, int(item.get("lessons", 0) or 0)), max(0, int(item.get("photos", 0) or 0)),
                text_value(item, "summary", 10000), text_value(item, "individual", 10000),
                text_value(item, "next", 10000), text_value(item, "status", 80), index,
            ),
        )
    connection.execute("DELETE FROM class_schedule")
    for item in weekly_schedule:
        lesson_id = required_id(item, "id", "시간표 수업")
        day = text_value(item, "day", 10)
        if day not in SCHEDULE_DAYS:
            raise ValueError("시간표 요일 정보가 올바르지 않습니다.")
        teacher_id = text_value(item, "teacherId", 80)
        if teacher_id and teacher_id not in teacher_ids:
            raise ValueError("시간표 담당 선생님 정보가 올바르지 않습니다.")
        linked_student_ids = item.get("studentIds") or []
        if not isinstance(linked_student_ids, list) or any(value not in student_ids for value in linked_student_ids):
            raise ValueError("시간표 학생 명단이 올바르지 않습니다.")
        teacher_name = next((teacher["name"] for teacher in teachers if teacher["id"] == teacher_id), "")
        linked_students = [student for student in students if student["id"] in linked_student_ids]
        connection.execute(
            """
            INSERT INTO class_schedule(
              id,day,start_time,end_time,time_label,class_name,subject,teacher_name,
              students_json,updated_at,teacher_id,student_ids_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                lesson_id, day, text_value(item, "start", 10), text_value(item, "end", 10),
                text_value(item, "timeLabel", 40), text_value(item, "className", 120),
                text_value(item, "subject", 120), teacher_name,
                json.dumps([
                    {"id": student["id"], "name": student["name"], "school": text_value(student, "school", 160)}
                    for student in linked_students
                ], ensure_ascii=False),
                iso_now(), teacher_id or None, json.dumps(linked_student_ids, ensure_ascii=False),
            ),
        )
    for index, item in enumerate(consultations):
        student_id = text_value(item, "studentId", 80)
        if student_id not in student_ids:
            raise ValueError("상담 기록의 학생 정보가 올바르지 않습니다.")
        connection.execute(
            """
            INSERT INTO consultations(
              id,consultation_date,student_id,consultation_type,summary,followup_date,created_at,sort_order
            ) VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                required_id(item, "id", "상담 기록"), text_value(item, "date", 10), student_id,
                text_value(item, "type", 40), text_value(item, "summary", 10000),
                text_value(item, "followup", 10), iso_now(), index,
            ),
        )
    connection.execute(
        """
        INSERT INTO academy_meta(key,value,updated_at) VALUES ('owner_state_initialized','1',?)
        ON CONFLICT(key) DO UPDATE SET value='1', updated_at=excluded.updated_at
        """,
        (iso_now(),),
    )


EVALUATION_FIELDS = (
    "attitude", "concentration", "understanding", "progress", "participation", "homework"
)
STUDENT_ATTENDANCE_LABELS = {
    "present": "출석",
    "late": "지각",
    "absent": "결석",
    "excused": "인정결석",
    "makeup": "보강",
}
EVALUATION_LABELS = {
    "attitude": ("보완 필요", "조금 아쉬움", "좋음", "매우 좋음"),
    "concentration": ("집중 어려움", "간헐적 집중", "잘 집중함", "매우 몰입함"),
    "understanding": ("추가 설명 필요", "반복 연습 필요", "잘 이해함", "응용 가능"),
    "progress": ("진도 보완", "조금 느림", "계획대로", "심화 가능"),
    "participation": ("소극적", "보통", "적극적", "주도적"),
    "homework": ("보완 필요", "일부 수행", "잘 수행함", "매우 충실함"),
}
EVALUATION_PHRASES = {
    "attitude": ("수업 태도는 조금 더 다듬을 필요가 있었고", "수업 태도는 조금 아쉬웠지만", "수업 태도가 좋았고", "수업 태도가 매우 좋았고"),
    "concentration": ("집중을 유지하는 데 도움이 필요했습니다", "중간중간 집중을 다시 잡아 주었습니다", "수업에 잘 집중했습니다", "수업에 매우 몰입했습니다"),
    "understanding": ("개념 이해를 위해 추가 설명이 필요했습니다", "반복해서 연습하면 이해가 더 안정될 단계입니다", "배운 내용을 잘 이해했습니다", "배운 내용을 응용할 수 있을 만큼 이해도가 좋았습니다"),
    "progress": ("진도를 보완하며 기초를 다시 확인했습니다", "진도를 조금 천천히 진행했습니다", "계획한 진도대로 진행했습니다", "계획보다 빠르게 이해해 심화 학습도 가능했습니다"),
    "participation": ("수업 참여를 조금 더 이끌어 줄 필요가 있었고", "필요한 활동에 차분히 참여했고", "수업에 적극적으로 참여했고", "스스로 질문하고 설명하며 주도적으로 참여했고"),
    "homework": ("과제는 보완이 필요했습니다", "과제는 일부 수행했습니다", "과제도 잘 수행했습니다", "과제를 매우 충실하게 수행했습니다"),
}


def evaluation_label(field: str, score: int) -> str:
    return EVALUATION_LABELS[field][max(1, min(4, int(score))) - 1]


def evaluation_phrase(field: str, score: int) -> str:
    return EVALUATION_PHRASES[field][max(1, min(4, int(score))) - 1]


def evaluation_as_dict(row: sqlite3.Row | dict) -> dict:
    item = dict(row)
    item["scores"] = {
        field: {
            "value": item[field],
            "label": evaluation_label(field, item[field]),
        }
        for field in EVALUATION_FIELDS
    }
    return item


def student_attendance_as_dict(row: sqlite3.Row | dict) -> dict:
    item = dict(row)
    item["attendance_label"] = STUDENT_ATTENDANCE_LABELS.get(
        item.get("attendance_status", ""), item.get("attendance_status", "")
    )
    return item


def template_feedback_message(evaluation: sqlite3.Row | dict) -> str:
    item = dict(evaluation)
    class_name = str(item.get("class_name", "")).strip()
    subject = str(item.get("subject", "")).strip()
    lesson = f"{class_name}에서 {subject}" if class_name and subject else class_name or subject or "오늘"
    observation = str(item.get("note", "")).strip()
    return (
        f"안녕하세요, {item.get('student_name', '학생')} 학부모님.\n\n"
        f"오늘 {lesson} 수업을 진행했습니다. "
        f"{evaluation_phrase('attitude', item['attitude'])} "
        f"{evaluation_phrase('concentration', item['concentration'])}. "
        f"{evaluation_phrase('understanding', item['understanding'])}.\n\n"
        f"{observation}\n\n"
        f"{evaluation_phrase('progress', item['progress'])}. "
        f"{evaluation_phrase('participation', item['participation'])} "
        f"{evaluation_phrase('homework', item['homework'])}. "
        "다음 수업에서도 오늘 확인한 강점은 이어가고 필요한 부분은 세심하게 지도하겠습니다."
    )


def extract_response_text(payload: dict) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    for output in payload.get("output") or []:
        if not isinstance(output, dict):
            continue
        for content in output.get("content") or []:
            if not isinstance(content, dict):
                continue
            text = content.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
    raise ValueError("AI 응답에서 메시지를 찾지 못했습니다.")


def feedback_prompt_context(item: dict) -> dict:
    """Only send lesson facts needed for the draft; omit contact and address data."""
    observation = str(item.get("note", ""))
    student_name = str(item.get("student_name", "")).strip()
    if student_name:
        observation = observation.replace(student_name, "학생")
    return {
        "class": item.get("class_name", ""),
        "subject": item.get("subject", ""),
        "scores": {
            field: evaluation_label(field, item[field]) for field in EVALUATION_FIELDS
        },
        "teacher_observation": observation,
    }


FEEDBACK_INSTRUCTIONS = (
    "당신은 학원 원장님의 학부모 안내문 작성 도우미입니다. 제공된 사실만 사용해 "
    "따뜻하고 구체적인 한국어 문장 3~5개를 작성하세요. 학생을 다른 학생과 비교하거나 "
    "의학적·심리적 진단을 하지 말고, 보완점은 존중하는 표현으로 바꾸세요. 인사말과 학생 이름은 "
    "서버가 별도로 붙이므로 본문만 작성하세요. 과장, 이모지, 마크다운 제목은 쓰지 마세요. "
    "반드시 message 문자열 하나만 가진 JSON 객체로 답하세요."
)


def codex_binary() -> str | None:
    configured = os.environ.get("ACADEMY_CODEX_CLI", "").strip()
    if configured:
        return configured if Path(configured).is_file() else None
    return shutil.which("codex")


def codex_login_ready() -> bool:
    binary = codex_binary()
    if not binary:
        return False
    try:
        result = subprocess.run(
            [binary, "login", "status"], capture_output=True, text=True, timeout=8, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def feedback_ai_status() -> dict:
    mode = os.environ.get("ACADEMY_FEEDBACK_AI_PROVIDER", "template").strip().lower()
    if mode not in {"template", "codex", "openai", "auto"}:
        mode = "template"
    codex_ready = codex_login_ready() if mode in {"codex", "auto"} else False
    api_ready = bool(os.environ.get("OPENAI_API_KEY", "").strip())
    if mode == "codex":
        active = "codex" if codex_ready else "template"
    elif mode == "openai":
        active = "openai" if api_ready else "template"
    elif mode == "auto":
        active = "codex" if codex_ready else "openai" if api_ready else "template"
    else:
        active = "template"
    return {
        "requested": mode,
        "active": active,
        "configured": active != "template",
        "codexReady": codex_ready,
        "openaiReady": api_ready,
    }


def codex_feedback_body(item: dict) -> str:
    binary = codex_binary()
    if not binary:
        raise RuntimeError("Codex 실행 파일을 찾지 못했습니다.")
    schema = {
        "type": "object",
        "properties": {"message": {"type": "string"}},
        "required": ["message"],
        "additionalProperties": False,
    }
    prompt = (
        f"{FEEDBACK_INSTRUCTIONS}\n\n수업 평가 자료:\n"
        f"{json.dumps(feedback_prompt_context(item), ensure_ascii=False)}"
    )
    with tempfile.TemporaryDirectory(prefix="easymath-codex-") as temp_name:
        temp_path = Path(temp_name)
        schema_path = temp_path / "feedback-schema.json"
        output_path = temp_path / "feedback-output.json"
        schema_path.write_text(json.dumps(schema, ensure_ascii=False), encoding="utf-8")
        command = [
            binary, "exec", "--ephemeral", "--sandbox", "read-only",
            "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
            "--output-schema", str(schema_path), "-o", str(output_path), "-",
        ]
        model = os.environ.get("ACADEMY_CODEX_FEEDBACK_MODEL", "").strip()
        if model:
            command[2:2] = ["--model", model]
        process_env = os.environ.copy()
        process_env.pop("OPENAI_API_KEY", None)
        with CODEX_FEEDBACK_LOCK:
            result = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=int(os.environ.get("ACADEMY_CODEX_TIMEOUT", "90")),
                check=False,
                cwd=temp_name,
                env=process_env,
            )
        if result.returncode != 0 or not output_path.exists():
            raise RuntimeError("Codex 초안 생성에 실패했습니다.")
        structured = json.loads(output_path.read_text(encoding="utf-8"))
    body = str(structured.get("message", "")).strip()
    if not body:
        raise ValueError("Codex 메시지가 비어 있습니다.")
    return body


def openai_feedback_body(item: dict) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OpenAI API 키가 설정되지 않았습니다.")
    request_body = {
        "model": os.environ.get("OPENAI_FEEDBACK_MODEL", "gpt-6-luna"),
        "store": False,
        "instructions": FEEDBACK_INSTRUCTIONS,
        "input": json.dumps(feedback_prompt_context(item), ensure_ascii=False),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "parent_feedback_message",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"],
                    "additionalProperties": False,
                },
            }
        },
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        response_payload = json.load(response)
    structured = json.loads(extract_response_text(response_payload))
    body = str(structured.get("message", "")).strip()
    if not body:
        raise ValueError("AI 메시지가 비어 있습니다.")
    return body


def generate_feedback_message(evaluation: sqlite3.Row | dict) -> tuple[str, str, str]:
    """Return (message, provider, notice), falling back without blocking operations."""
    item = dict(evaluation)
    mode = os.environ.get("ACADEMY_FEEDBACK_AI_PROVIDER", "template").strip().lower()
    providers = ["codex", "openai"] if mode == "auto" else [mode]
    for provider in providers:
        try:
            if provider == "codex" and codex_login_ready():
                body = codex_feedback_body(item)
                message = f"안녕하세요, {item.get('student_name', '학생')} 학부모님.\n\n{body}"
                return message, "codex", "Codex 초안을 만들었습니다. 원장님이 확인하고 수정해 주세요."
            if provider == "openai" and os.environ.get("OPENAI_API_KEY", "").strip():
                body = openai_feedback_body(item)
                message = f"안녕하세요, {item.get('student_name', '학생')} 학부모님.\n\n{body}"
                return message, "openai", "AI 초안을 만들었습니다. 원장님이 확인하고 수정해 주세요."
        except (
            OSError, RuntimeError, subprocess.TimeoutExpired, urllib.error.URLError,
            TimeoutError, ValueError, KeyError, json.JSONDecodeError,
        ):
            continue
    return template_feedback_message(item), "template", "AI 연결 전이거나 생성에 실패해 기본 초안을 만들었습니다."


def messaging_connector_configuration() -> dict:
    """Describe the optional personal-Kakao connector without auto-selecting this computer."""
    url = os.environ.get("ACADEMY_MESSAGING_CONNECTOR_URL", "").strip().rstrip("/")
    cli = os.environ.get("ACADEMY_MESSAGING_CONNECTOR_CLI", "").strip()
    if url:
        return {"kind": "http", "target": url}
    if cli and Path(cli).is_file():
        return {"kind": "cli", "target": cli}
    return {"kind": "none", "target": ""}


def connector_http_request(method: str, path: str, payload: dict | None = None) -> dict | list:
    config = messaging_connector_configuration()
    if config["kind"] != "http":
        raise RuntimeError("메시지 연결기가 설정되지 않았습니다.")
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    token = os.environ.get("ACADEMY_MESSAGING_CONNECTOR_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        f"{config['target']}{path}", data=body, headers=headers, method=method
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def connector_cli_json(arguments: list[str], timeout: int = 30) -> dict | list:
    config = messaging_connector_configuration()
    if config["kind"] != "cli":
        raise RuntimeError("메시지 연결기가 설정되지 않았습니다.")
    result = subprocess.run(
        [config["target"], *arguments], capture_output=True, text=True, timeout=timeout, check=False
    )
    if result.returncode != 0:
        raise RuntimeError("메시지 연결기 실행에 실패했습니다.")
    return json.loads(result.stdout)


def normalized_connector_rooms(payload: dict | list) -> list[dict]:
    raw_rooms = payload if isinstance(payload, list) else payload.get("rooms", payload.get("chats", []))
    rooms = []
    for item in raw_rooms if isinstance(raw_rooms, list) else []:
        if not isinstance(item, dict):
            continue
        chat_id = str(item.get("chat_id", item.get("id", ""))).strip()
        title = str(item.get("title", item.get("name", ""))).strip()
        if chat_id and title:
            rooms.append({"chatId": chat_id[:500], "title": title[:300]})
    return rooms


def messaging_connector_status() -> dict:
    config = messaging_connector_configuration()
    if config["kind"] == "none":
        return {"configured": False, "ready": False, "kind": "none"}
    try:
        if config["kind"] == "http":
            payload = connector_http_request("GET", "/status")
            ready = bool(payload.get("ready")) if isinstance(payload, dict) else False
        else:
            result = subprocess.run(
                [config["target"], "status"], capture_output=True, text=True, timeout=10, check=False
            )
            ready = result.returncode == 0
    except (OSError, RuntimeError, subprocess.TimeoutExpired, urllib.error.URLError, ValueError, json.JSONDecodeError):
        ready = False
    return {"configured": True, "ready": ready, "kind": config["kind"]}


def messaging_connector_rooms() -> list[dict]:
    config = messaging_connector_configuration()
    if config["kind"] == "http":
        payload = connector_http_request("GET", "/rooms")
    elif config["kind"] == "cli":
        payload = connector_cli_json(["chats", "--json", "--limit", "100"])
    else:
        raise RuntimeError("메시지 연결기를 먼저 설정해 주세요.")
    return normalized_connector_rooms(payload)


def messaging_connector_messages(chat_id: str, limit: int = 20) -> list[dict]:
    config = messaging_connector_configuration()
    safe_limit = max(1, min(50, int(limit)))
    if config["kind"] == "http":
        payload = connector_http_request(
            "GET", f"/messages?{urllib.parse.urlencode({'chat_id': chat_id, 'limit': safe_limit})}"
        )
    elif config["kind"] == "cli":
        payload = connector_cli_json(
            ["read", "--chat-id", chat_id, "--limit", str(safe_limit), "--json"], timeout=45
        )
    else:
        raise RuntimeError("메시지 연결기를 먼저 설정해 주세요.")
    raw_messages = payload if isinstance(payload, list) else payload.get("messages", [])
    messages = []
    for item in raw_messages if isinstance(raw_messages, list) else []:
        if not isinstance(item, dict):
            continue
        messages.append({
            "author": str(item.get("author", item.get("sender", "")))[:200],
            "text": str(item.get("text", item.get("message", "")))[:6000],
            "timestamp": str(item.get("timestamp", item.get("time", "")))[:100],
        })
    return messages


def messaging_connector_send(chat_id: str, message: str) -> bool:
    config = messaging_connector_configuration()
    if config["kind"] == "http":
        payload = connector_http_request(
            "POST", "/send", {"chat_id": chat_id, "message": message}
        )
        return isinstance(payload, dict) and payload.get("status") == "sent"
    if config["kind"] == "cli":
        result = subprocess.run(
            [config["target"], "send", "--chat-id", chat_id, "--", message],
            capture_output=True, text=True, timeout=45, check=False,
        )
        return result.returncode == 0 and "message sent" in result.stdout.lower()
    raise RuntimeError("메시지 연결기를 먼저 설정해 주세요.")


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def kiosk_bearer_token(headers) -> str:
    authorization = str(headers.get("Authorization", ""))
    if not authorization.startswith("Bearer "):
        return ""
    return authorization.removeprefix("Bearer ").strip()


def kiosk_device_for_token(token: str | None):
    if not token:
        return None
    with db() as connection:
        device = connection.execute(
            "SELECT id,name,active,created_at,last_seen_at FROM kiosk_devices WHERE token_hash=? AND active=1",
            (token_hash(token),),
        ).fetchone()
        if device:
            connection.execute(
                "UPDATE kiosk_devices SET last_seen_at=? WHERE id=?", (iso_now(), device["id"])
            )
    return device


def limited_attempt(store: dict[str, list[float]], key: str, limit: int, window: int) -> bool:
    current = time.time()
    attempts = [stamp for stamp in store.get(key, []) if current - stamp < window]
    store[key] = attempts
    return len(attempts) >= limit


def note_failed_attempt(store: dict[str, list[float]], key: str) -> None:
    attempts = store.setdefault(key, [])
    attempts.append(time.time())


def create_kiosk_pairing_code(connection: sqlite3.Connection, valid_seconds: int = 600) -> dict:
    connection.execute("DELETE FROM kiosk_pairing_codes WHERE expires_at<? OR used_at IS NOT NULL", (int(time.time()),))
    for _ in range(20):
        code = f"{secrets.randbelow(1_000_000):06d}"
        hashed = token_hash(f"kiosk-pair:{code}")
        try:
            connection.execute(
                "INSERT INTO kiosk_pairing_codes(code_hash,expires_at) VALUES (?,?)",
                (hashed, int(time.time()) + valid_seconds),
            )
            return {"code": code, "expiresAt": int(time.time()) + valid_seconds}
        except sqlite3.IntegrityError:
            continue
    raise RuntimeError("연결코드를 만들지 못했습니다. 잠시 뒤 다시 시도해 주세요.")


def pair_kiosk_device(connection: sqlite3.Connection, code: str, device_name: str) -> dict:
    digits = "".join(character for character in str(code or "") if character.isdigit())
    name = str(device_name or "").strip()[:80] or "등원 태블릿"
    if len(digits) != 6:
        raise ValueError("원장 화면의 6자리 연결코드를 입력해 주세요.")
    hashed_code = token_hash(f"kiosk-pair:{digits}")
    row = connection.execute(
        "SELECT expires_at,used_at FROM kiosk_pairing_codes WHERE code_hash=?", (hashed_code,)
    ).fetchone()
    if not row or row["used_at"] or row["expires_at"] < int(time.time()):
        raise ValueError("연결코드가 올바르지 않거나 만료되었습니다.")
    token = secrets.token_urlsafe(40)
    device_id = f"kiosk-{secrets.token_hex(12)}"
    timestamp = iso_now()
    connection.execute(
        "INSERT INTO kiosk_devices(id,name,token_hash,created_at,last_seen_at) VALUES (?,?,?,?,?)",
        (device_id, name, token_hash(token), timestamp, timestamp),
    )
    connection.execute(
        "UPDATE kiosk_pairing_codes SET used_at=? WHERE code_hash=?", (timestamp, hashed_code)
    )
    return {"token": token, "device": {"id": device_id, "name": name}}


def student_checkin_code(row: sqlite3.Row | dict) -> str:
    item = dict(row)
    student_phone = normalize_phone(item.get("phone"))
    return student_phone[-4:] if len(student_phone) >= 4 else ""


def record_student_checkin(
    connection: sqlite3.Connection, code: str, device_id: str, current: datetime | None = None,
    selected_student_id: str = "",
) -> dict:
    digits = "".join(character for character in str(code or "") if character.isdigit())
    if len(digits) != 4:
        raise ValueError("전화번호 뒤 4자리를 입력해 주세요.")
    students = connection.execute(
        "SELECT id,name,phone,guardian_phone,checkin_code FROM academy_students WHERE status='재원' ORDER BY sort_order,id"
    ).fetchall()
    matches = [student for student in students if student_checkin_code(student) == digits]
    if not matches:
        raise LookupError("일치하는 학생을 찾지 못했습니다. 데스크에 문의해 주세요.")
    if len(matches) > 1 and not selected_student_id:
        return {
            "selectionRequired": True,
            "candidates": [{"studentId": student["id"], "studentName": student["name"]} for student in matches],
        }
    student = next((item for item in matches if item["id"] == selected_student_id), None) if selected_student_id else matches[0]
    if not student:
        raise ValueError("선택한 학생과 입력한 전화번호가 일치하지 않습니다. 다시 입력해 주세요.")
    checkin_time = current or now_kst()
    duplicate_after = (checkin_time - timedelta(hours=2)).isoformat(timespec="seconds")
    previous = connection.execute(
        """
        SELECT * FROM student_checkins
        WHERE student_id=? AND checked_in_at>=?
        ORDER BY checked_in_at DESC LIMIT 1
        """,
        (student["id"], duplicate_after),
    ).fetchone()
    if previous:
        return {
            "id": previous["id"], "studentId": student["id"], "studentName": student["name"],
            "checkedInAt": previous["checked_in_at"], "notificationStatus": previous["notification_status"],
            "duplicate": True,
        }
    checkin_id = f"checkin-{checkin_time.strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(5)}"
    checked_in_at = checkin_time.isoformat(timespec="seconds")
    connection.execute(
        """
        INSERT INTO student_checkins(
          id,student_id,student_name,checkin_date,checked_in_at,device_id,notification_status
        ) VALUES (?,?,?,?,?,?,'pending')
        """,
        (checkin_id, student["id"], student["name"], checkin_time.date().isoformat(), checked_in_at, device_id),
    )
    return {
        "id": checkin_id, "studentId": student["id"], "studentName": student["name"],
        "checkedInAt": checked_in_at, "notificationStatus": "pending", "duplicate": False,
    }


def checkin_notification_message(student_name: str, checked_in_at: str) -> str:
    checked = datetime.fromisoformat(checked_in_at)
    period = "오전" if checked.hour < 12 else "오후"
    hour = checked.hour if 1 <= checked.hour <= 12 else (12 if checked.hour in {0, 12} else checked.hour - 12)
    return (
        f"안녕하세요. {student_name} 학생이 {checked.year}년 {checked.month}월 {checked.day}일 "
        f"{period} {hour}:{checked.minute:02d} 이지매쓰에 등원했습니다."
    )


def deliver_checkin_notification(checkin_id: str) -> None:
    with db() as connection:
        row = connection.execute(
            """
            SELECT c.*,r.chat_id,r.room_title
            FROM student_checkins c
            LEFT JOIN kakao_parent_rooms r ON r.student_id=c.student_id
            WHERE c.id=?
            """,
            (checkin_id,),
        ).fetchone()
    if not row or row["notification_status"] != "pending":
        return
    message = checkin_notification_message(row["student_name"], row["checked_in_at"])
    if not row["chat_id"]:
        with db() as connection:
            connection.execute(
                "UPDATE student_checkins SET notification_status='not_linked',notification_message=?,notification_finished_at=? WHERE id=?",
                (message, iso_now(), checkin_id),
            )
        return
    if messaging_connector_configuration()["kind"] == "none":
        with db() as connection:
            connection.execute(
                "UPDATE student_checkins SET notification_status='not_configured',notification_message=?,notification_finished_at=? WHERE id=?",
                (message, iso_now(), checkin_id),
            )
        return
    if not KAKAO_SEND_LOCK.acquire(timeout=60):
        with db() as connection:
            connection.execute(
                "UPDATE student_checkins SET notification_status='unknown',notification_message=?,notification_finished_at=? WHERE id=?",
                (message, iso_now(), checkin_id),
            )
        return
    log_id = f"checkin-notify:{checkin_id}"
    attempted_at = iso_now()
    try:
        with db() as connection:
            connection.execute(
                "UPDATE student_checkins SET notification_status='sending',notification_message=? WHERE id=?",
                (message, checkin_id),
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO kakao_send_log(
                  id,evaluation_id,student_id,chat_id,room_title,message,status,attempted_at
                ) VALUES (?,?,?,?,?,?,?,?)
                """,
                (log_id, f"checkin:{checkin_id}", row["student_id"], row["chat_id"], row["room_title"], message, "sending", attempted_at),
            )
        try:
            sent = messaging_connector_send(row["chat_id"], message)
        except (OSError, RuntimeError, subprocess.TimeoutExpired, urllib.error.URLError, ValueError, json.JSONDecodeError):
            sent = False
        status = "sent" if sent else "unknown"
        finished_at = iso_now()
        with db() as connection:
            connection.execute(
                "UPDATE student_checkins SET notification_status=?,notification_finished_at=? WHERE id=?",
                (status, finished_at, checkin_id),
            )
            connection.execute(
                "UPDATE kakao_send_log SET status=?,finished_at=? WHERE id=?",
                (status, finished_at, log_id),
            )
    finally:
        KAKAO_SEND_LOCK.release()


def report_period(value: str, base_date: str) -> tuple[date, date, str]:
    try:
        selected = datetime.strptime(base_date, "%Y-%m-%d").date()
    except (TypeError, ValueError) as error:
        raise ValueError("조회 날짜가 올바르지 않습니다.") from error
    if value == "week":
        start = selected - timedelta(days=selected.weekday())
        return start, start + timedelta(days=6), "주간"
    if value == "month":
        start = selected.replace(day=1)
        following = date(start.year + 1, 1, 1) if start.month == 12 else date(start.year, start.month + 1, 1)
        return start, following - timedelta(days=1), "월간"
    raise ValueError("리포트 기간은 주간 또는 월간이어야 합니다.")


def build_checkin_report(connection: sqlite3.Connection, period: str, base_date: str) -> dict:
    start, end, label = report_period(period, base_date)
    event_rows = connection.execute(
        """
        SELECT * FROM student_checkins
        WHERE checkin_date BETWEEN ? AND ?
        ORDER BY checked_in_at DESC
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    current_students = {
        row["id"]: dict(row)
        for row in connection.execute(
            """
            SELECT s.id,s.name,s.status,s.sort_order,r.room_title,
                   CASE WHEN r.chat_id IS NULL THEN 0 ELSE 1 END AS messaging_linked
            FROM academy_students s LEFT JOIN kakao_parent_rooms r ON r.student_id=s.id
            WHERE s.status='재원' ORDER BY s.sort_order,s.name
            """
        )
    }
    events_by_student: dict[str, list[dict]] = {}
    for row in event_rows:
        events_by_student.setdefault(row["student_id"], []).append(dict(row))
        current_students.setdefault(row["student_id"], {
            "id": row["student_id"], "name": row["student_name"], "status": "기록 보존",
            "sort_order": 99999, "room_title": None, "messaging_linked": 0,
        })
    planned_days: dict[str, set[str]] = {student_id: set() for student_id in current_students}
    schedule_rows = connection.execute("SELECT day,student_ids_json,students_json FROM class_schedule").fetchall()
    schedule_students_by_day: dict[str, set[str]] = {day: set() for day in DAY_KEYS}
    for row in schedule_rows:
        student_ids = json_list(row["student_ids_json"])
        if not student_ids:
            student_ids = [item.get("id") for item in json_list(row["students_json"]) if item.get("id")]
        schedule_students_by_day.setdefault(row["day"], set()).update(student_ids)
    cursor = start
    while cursor <= end:
        day_key = DAY_KEYS[cursor.weekday()]
        for student_id in schedule_students_by_day.get(day_key, set()):
            if student_id in planned_days:
                planned_days[student_id].add(cursor.isoformat())
        cursor += timedelta(days=1)
    student_reports = []
    for student in sorted(current_students.values(), key=lambda item: (item.get("sort_order", 99999), item["name"])):
        events = sorted(events_by_student.get(student["id"], []), key=lambda item: item["checked_in_at"])
        unique_dates = sorted({item["checkin_date"] for item in events})
        times = [datetime.fromisoformat(item["checked_in_at"]).strftime("%H:%M") for item in events]
        planned = len(planned_days.get(student["id"], set()))
        rate = round(len(unique_dates) / planned * 100) if planned else None
        period_text = f"{start.month}월 {start.day}일~{end.month}월 {end.day}일"
        attendance_text = f"예정 수업일 {planned}일 중 {len(unique_dates)}일 등원" if planned else f"총 {len(unique_dates)}일 등원"
        detail = ", ".join(
            f"{datetime.fromisoformat(item['checked_in_at']).month}/{datetime.fromisoformat(item['checked_in_at']).day} {datetime.fromisoformat(item['checked_in_at']).strftime('%H:%M')}"
            for item in events
        ) or "등원 기록 없음"
        message = (
            f"안녕하세요, {student['name']} 학부모님.\n\n"
            f"[{label} 등원 리포트 · {period_text}]\n{attendance_text}했습니다.\n"
            f"등원 기록: {detail}\n\n이지매쓰에서 보내드립니다."
        )
        student_reports.append({
            "studentId": student["id"], "studentName": student["name"],
            "checkinDays": len(unique_dates), "checkinCount": len(events),
            "plannedDays": planned, "attendanceRate": rate,
            "firstTime": times[0] if times else "", "lastTime": times[-1] if times else "",
            "events": [{"id": item["id"], "checkedInAt": item["checked_in_at"], "notificationStatus": item["notification_status"]} for item in events],
            "messagingLinked": bool(student.get("messaging_linked")),
            "messagingRoomTitle": student.get("room_title") or "",
            "message": message,
        })
    sent_count = sum(1 for item in event_rows if item["notification_status"] == "sent")
    attention_count = sum(1 for item in event_rows if item["notification_status"] in {"unknown", "not_linked", "not_configured"})
    today_count = connection.execute(
        "SELECT COUNT(DISTINCT student_id) AS count FROM student_checkins WHERE checkin_date=?",
        (now_kst().date().isoformat(),),
    ).fetchone()["count"]
    return {
        "period": period, "periodLabel": label, "startDate": start.isoformat(), "endDate": end.isoformat(),
        "summary": {
            "totalCheckins": len(event_rows), "uniqueStudents": len(events_by_student),
            "notificationsSent": sent_count, "notificationsAttention": attention_count,
            "todayCheckins": today_count,
        },
        "students": student_reports,
        "recent": [
            {
                "id": row["id"], "studentId": row["student_id"], "studentName": row["student_name"],
                "checkedInAt": row["checked_in_at"], "notificationStatus": row["notification_status"],
            }
            for row in event_rows[:100]
        ],
    }


def make_session(teacher_id: str) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + 60 * 60 * 24 * 30
    with db() as connection:
        connection.execute("DELETE FROM sessions WHERE expires_at < ?", (int(time.time()),))
        connection.execute(
            "INSERT INTO sessions(token_hash, teacher_id, expires_at) VALUES (?, ?, ?)",
            (token_hash(token), teacher_id, expires_at),
        )
    return token


def teacher_for_token(token: str | None):
    if not token:
        return None
    with db() as connection:
        return connection.execute(
            """
            SELECT t.* FROM sessions s
            JOIN teachers t ON t.id = s.teacher_id
            WHERE s.token_hash = ? AND s.expires_at >= ? AND t.active = 1
            """,
            (token_hash(token), int(time.time())),
        ).fetchone()


def owner_is_configured() -> bool:
    with db() as connection:
        return connection.execute("SELECT 1 FROM owner_accounts LIMIT 1").fetchone() is not None


def owner_login_required() -> bool:
    return os.environ.get("ACADEMY_REQUIRE_OWNER_LOGIN") == "1"


def owner_for_token(token: str | None):
    if not token:
        return None
    with db() as connection:
        return connection.execute(
            """
            SELECT a.username FROM owner_sessions s
            JOIN owner_accounts a ON a.username=s.username
            WHERE s.token_hash=? AND s.expires_at>=?
            """,
            (token_hash(token), int(time.time())),
        ).fetchone()


def verify_owner_password(username: str, password: str) -> bool:
    with db() as connection:
        row = connection.execute(
            "SELECT * FROM owner_accounts WHERE username=?",
            (username,),
        ).fetchone()
    if not row:
        hashlib.pbkdf2_hmac("sha256", password.encode(), b"missing-owner", OWNER_PASSWORD_ITERATIONS)
        return False
    expected = bytes.fromhex(row["password_hash"])
    actual = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(row["password_salt"]),
        row["iterations"],
    )
    return hmac.compare_digest(actual, expected)


def set_owner_password(password: str, username: str = "owner") -> None:
    if len(password) < 4:
        raise ValueError("원장 비밀번호는 4자 이상이어야 합니다.")
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, OWNER_PASSWORD_ITERATIONS
    )
    with db() as connection:
        connection.execute(
            """
            INSERT INTO owner_accounts(username,password_hash,password_salt,iterations,updated_at)
            VALUES (?,?,?,?,?)
            ON CONFLICT(username) DO UPDATE SET
              password_hash=excluded.password_hash,
              password_salt=excluded.password_salt,
              iterations=excluded.iterations,
              updated_at=excluded.updated_at
            """,
            (username, password_hash.hex(), salt.hex(), OWNER_PASSWORD_ITERATIONS, iso_now()),
        )
        connection.execute("DELETE FROM owner_sessions WHERE username=?", (username,))


def make_owner_session(username: str) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + 60 * 60 * 12
    with db() as connection:
        connection.execute("DELETE FROM owner_sessions WHERE expires_at < ?", (int(time.time()),))
        connection.execute(
            "INSERT INTO owner_sessions(token_hash,username,expires_at,created_at) VALUES (?,?,?,?)",
            (token_hash(token), username, expires_at, iso_now()),
        )
    return token


class AcademyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json_with_cookie(self, payload, cookie, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def send_redirect(self, location, cookie=None):
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 10_000_000:
            raise ValueError("요청이 너무 큽니다.")
        return json.loads(self.rfile.read(length) or b"{}")

    def cookies(self):
        jar = http.cookies.SimpleCookie()
        jar.load(self.headers.get("Cookie", ""))
        return {key: morsel.value for key, morsel in jar.items()}

    def current_teacher(self):
        return teacher_for_token(self.cookies().get(SESSION_COOKIE))

    def teacher_cookie(self, token: str, max_age: int = 60 * 60 * 24 * 30) -> str:
        secure = "; Secure" if os.environ.get("ACADEMY_HTTPS") == "1" else ""
        return (
            f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; "
            f"Max-Age={max_age}{secure}"
        )

    def current_owner(self):
        return owner_for_token(self.cookies().get(OWNER_SESSION_COOKIE))

    def current_kiosk_device(self):
        return kiosk_device_for_token(kiosk_bearer_token(self.headers))

    def owner_allowed(self):
        if owner_is_configured():
            return self.current_owner() is not None
        if owner_login_required():
            return False
        return self.client_address[0] in {"127.0.0.1", "::1"}

    def owner_cookie(self, token: str, max_age: int = 60 * 60 * 12) -> str:
        secure = "; Secure" if os.environ.get("ACADEMY_HTTPS") == "1" else ""
        return (
            f"{OWNER_SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; "
            f"Max-Age={max_age}{secure}"
        )

    def receive_photos(self):
        if not self.owner_allowed():
            self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 사용할 수 있습니다."}, HTTPStatus.FORBIDDEN)
            return
        content_type = self.headers.get("Content-Type", "")
        length = int(self.headers.get("Content-Length", "0"))
        if not content_type.lower().startswith("multipart/form-data"):
            self.send_json({"error": "사진 업로드 형식이 올바르지 않습니다."}, HTTPStatus.BAD_REQUEST)
            return
        if length <= 0 or length > MAX_PHOTO_REQUEST_BYTES:
            self.send_json({"error": "한 번에 올릴 수 있는 사진은 최대 60MB입니다."}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        body = self.rfile.read(length)
        message = BytesParser(policy=policy.default).parsebytes(
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
        )
        saved_paths: list[Path] = []
        uploaded = []
        try:
            parts = list(message.iter_parts()) if message.is_multipart() else []
            file_parts = [part for part in parts if part.get_filename()]
            if not file_parts or len(file_parts) > 10:
                raise ValueError("사진은 한 번에 1장부터 10장까지 첨부할 수 있습니다.")
            for part in file_parts:
                original_name = Path(str(part.get_filename()).replace("\\", "/")).name[:255]
                mime_type = part.get_content_type().lower()
                data = part.get_payload(decode=True) or b""
                if mime_type not in ALLOWED_IMAGE_TYPES:
                    raise ValueError(f"지원하지 않는 사진 형식입니다: {original_name}")
                if not data or len(data) > MAX_PHOTO_BYTES:
                    raise ValueError(f"사진 한 장은 15MB 이하여야 합니다: {original_name}")
                stored_name = f"{now_kst().strftime('%Y%m%d')}-{secrets.token_hex(16)}{ALLOWED_IMAGE_TYPES[mime_type]}"
                target = PHOTO_PATH / stored_name
                with target.open("xb") as photo_file:
                    photo_file.write(data)
                saved_paths.append(target)
                uploaded.append({
                    "originalName": original_name,
                    "storedName": stored_name,
                    "mimeType": mime_type,
                    "size": len(data),
                    "url": f"/media/{urllib.parse.quote(stored_name)}",
                })
        except (OSError, ValueError) as error:
            for path in saved_paths:
                try:
                    path.unlink()
                except OSError:
                    pass
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"ok": True, "photos": uploaded}, HTTPStatus.CREATED)

    def send_photo(self, stored_name: str):
        if not self.owner_allowed():
            self.send_json({"error": "원장 로그인이 필요합니다."}, HTTPStatus.FORBIDDEN)
            return
        if Path(stored_name).name != stored_name:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        with db() as connection:
            row = connection.execute(
                "SELECT mime_type FROM lesson_record_photos WHERE stored_name=? LIMIT 1",
                (stored_name,),
            ).fetchone()
        path = PHOTO_PATH / stored_name
        if not row or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        mime_type = row["mime_type"] or mimetypes.guess_type(stored_name)[0] or "application/octet-stream"
        size = path.stat().st_size
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(size))
        self.send_header("Cache-Control", "private, no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        with path.open("rb") as photo_file:
            while chunk := photo_file.read(64 * 1024):
                self.wfile.write(chunk)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith("/media/"):
            self.send_photo(urllib.parse.unquote(path.removeprefix("/media/")))
            return

        if path == "/api/kiosk/status":
            device = self.current_kiosk_device()
            if not device:
                self.send_json({"paired": False}, HTTPStatus.UNAUTHORIZED)
                return
            self.send_json({"paired": True, "device": {"id": device["id"], "name": device["name"]}})
            return

        if path in {"/", "/index.html"} and (owner_is_configured() or owner_login_required()) and not self.current_owner():
            self.send_redirect("/owner-login.html")
            return

        if path == "/api/config":
            ai_status = feedback_ai_status()
            connector_status = messaging_connector_status()
            self.send_json({
                "kakaoConfigured": bool(os.environ.get("KAKAO_REST_API_KEY")),
                "teacherApp": "/teacher.html",
                "ownerConfigured": owner_is_configured(),
                "feedbackAiConfigured": ai_status["configured"],
                "feedbackAiProvider": ai_status["active"],
                "feedbackAiRequestedProvider": ai_status["requested"],
                "messagingConnector": connector_status,
            })
            return
        if path == "/api/owner/session":
            configured = owner_is_configured()
            owner = self.current_owner() if configured else None
            self.send_json({
                "configured": configured,
                "authenticated": bool(owner) or (not configured and not owner_login_required()),
                "username": owner["username"] if owner else None,
            })
            return
        if path == "/api/teacher/me":
            teacher = self.current_teacher()
            if not teacher:
                self.send_json({"authenticated": False}, HTTPStatus.UNAUTHORIZED)
                return
            self.send_json({"authenticated": True, "teacher": dict(teacher)})
            return
        if path == "/api/teacher/history":
            teacher = self.current_teacher()
            if not teacher:
                self.send_json({"error": "로그인이 필요합니다."}, HTTPStatus.UNAUTHORIZED)
                return
            with db() as connection:
                rows = connection.execute(
                    "SELECT * FROM attendance_requests WHERE teacher_id = ? ORDER BY requested_at DESC LIMIT 60",
                    (teacher["id"],),
                ).fetchall()
                adjustments = connection.execute(
                    """
                    SELECT * FROM attendance_adjustment_requests
                    WHERE teacher_id=? ORDER BY requested_at DESC LIMIT 60
                    """,
                    (teacher["id"],),
                ).fetchall()
                work_schedule = connection.execute(
                    """
                    SELECT day,start_time,end_time,break_minutes,note
                    FROM teacher_work_schedule WHERE academy_teacher_id=?
                    ORDER BY CASE day
                      WHEN 'mon' THEN 1 WHEN 'tue' THEN 2 WHEN 'wed' THEN 3
                      WHEN 'thu' THEN 4 WHEN 'fri' THEN 5 WHEN 'sat' THEN 6 ELSE 7 END
                    """,
                    (teacher["academy_teacher_id"] or "",),
                ).fetchall()
            today_key = DAY_KEYS[now_kst().weekday()]
            today_schedule = next((dict(row) for row in work_schedule if row["day"] == today_key), None)
            today = now_kst().date().isoformat()
            approved_change = next((
                row for row in adjustments
                if row["work_date"] == today
                and row["request_type"] == "schedule_change"
                and row["status"] == "approved"
            ), None)
            if today_schedule and approved_change:
                today_schedule.update({
                    "start_time": approved_change["start_time"],
                    "end_time": approved_change["end_time"],
                    "note": "승인된 날짜별 근무시간 변경",
                    "is_override": True,
                })
            self.send_json({
                "requests": [dict(row) for row in rows],
                "adjustments": [dict(row) for row in adjustments],
                "workSchedule": [dict(row) for row in work_schedule],
                "todaySchedule": today_schedule,
            })
            return
        if path == "/api/teacher/schedule":
            teacher = self.current_teacher()
            if not teacher:
                self.send_json({"error": "로그인이 필요합니다."}, HTTPStatus.UNAUTHORIZED)
                return
            with db() as connection:
                rows = connection.execute(
                    """
                    SELECT id, day, start_time, end_time, time_label, class_name, subject, students_json
                    FROM class_schedule
                    WHERE teacher_id = COALESCE(?, '')
                       OR (COALESCE(teacher_id, '') = '' AND teacher_name = ?)
                    ORDER BY CASE day
                      WHEN 'mon' THEN 1 WHEN 'tue' THEN 2 WHEN 'wed' THEN 3
                      WHEN 'thu' THEN 4 WHEN 'fri' THEN 5 WHEN 'sat' THEN 6 ELSE 7 END,
                      start_time
                    """,
                    (teacher["academy_teacher_id"], teacher["name"]),
                ).fetchall()
            lessons = []
            for row in rows:
                lesson = dict(row)
                lesson["students"] = json.loads(lesson.pop("students_json"))
                lessons.append(lesson)
            self.send_json({"lessons": lessons})
            return
        if path == "/api/teacher/evaluations":
            teacher = self.current_teacher()
            if not teacher:
                self.send_json({"error": "로그인이 필요합니다."}, HTTPStatus.UNAUTHORIZED)
                return
            lesson_date = query.get("date", [now_kst().date().isoformat()])[0]
            try:
                day = day_key_for_date(lesson_date)
            except ValueError as error:
                self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
                return
            with db() as connection:
                rows = connection.execute(
                    """
                    SELECT id,day,start_time,end_time,time_label,class_name,subject,students_json
                    FROM class_schedule
                    WHERE day=? AND (
                      teacher_id=COALESCE(?, '') OR
                      (COALESCE(teacher_id, '')='' AND teacher_name=?)
                    )
                    ORDER BY start_time,id
                    """,
                    (day, teacher["academy_teacher_id"], teacher["name"]),
                ).fetchall()
                evaluations = connection.execute(
                    """
                    SELECT * FROM student_evaluations
                    WHERE teacher_id=? AND lesson_date=?
                    ORDER BY updated_at
                    """,
                    (teacher["id"], lesson_date),
                ).fetchall()
                attendance_records = connection.execute(
                    """
                    SELECT * FROM student_attendance_records
                    WHERE teacher_id=? AND lesson_date=?
                    ORDER BY updated_at
                    """,
                    (teacher["id"], lesson_date),
                ).fetchall()
            evaluation_map = {
                (row["lesson_id"], row["student_id"]): evaluation_as_dict(row)
                for row in evaluations
            }
            attendance_map = {
                (row["lesson_id"], row["student_id"]): student_attendance_as_dict(row)
                for row in attendance_records
            }
            lessons = []
            for row in rows:
                lesson = dict(row)
                students = json_list(lesson.pop("students_json"))
                lesson["students"] = [
                    {
                        **student,
                        "evaluation": evaluation_map.get((lesson["id"], str(student.get("id", "")))),
                        "attendance": attendance_map.get((lesson["id"], str(student.get("id", "")))),
                    }
                    for student in students
                ]
                lessons.append(lesson)
            self.send_json({"date": lesson_date, "lessons": lessons})
            return
        if path == "/api/owner/evaluations":
            if not self.owner_allowed():
                self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 열 수 있습니다."}, HTTPStatus.FORBIDDEN)
                return
            lesson_date = query.get("date", [""])[0].strip()
            student_id = query.get("studentId", [""])[0].strip()[:80]
            clauses = []
            parameters: list[str] = []
            if lesson_date:
                try:
                    datetime.strptime(lesson_date, "%Y-%m-%d")
                except ValueError:
                    self.send_json({"error": "조회 날짜가 올바르지 않습니다."}, HTTPStatus.BAD_REQUEST)
                    return
                clauses.append("e.lesson_date=?")
                parameters.append(lesson_date)
            if student_id:
                clauses.append("e.student_id=?")
                parameters.append(student_id)
            where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            with db() as connection:
                rows = connection.execute(
                    f"""
                    SELECT e.*,r.room_title AS messaging_room_title,
                           CASE WHEN r.chat_id IS NULL THEN 0 ELSE 1 END AS messaging_linked
                    FROM student_evaluations e
                    LEFT JOIN kakao_parent_rooms r ON r.student_id=e.student_id
                    {where}
                    ORDER BY e.lesson_date DESC, e.updated_at DESC LIMIT 500
                    """,
                    parameters,
                ).fetchall()
            self.send_json({"evaluations": [evaluation_as_dict(row) for row in rows]})
            return
        if path == "/api/owner/messaging/links":
            if not self.owner_allowed():
                self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 열 수 있습니다."}, HTTPStatus.FORBIDDEN)
                return
            with db() as connection:
                rows = connection.execute(
                    """
                    SELECT r.student_id,r.room_title,r.linked_at,r.updated_at,s.name AS student_name
                    FROM kakao_parent_rooms r
                    LEFT JOIN academy_students s ON s.id=r.student_id
                    ORDER BY COALESCE(s.sort_order,99999),COALESCE(s.name,r.student_id)
                    """
                ).fetchall()
            self.send_json({
                "connector": messaging_connector_status(),
                "links": [dict(row) for row in rows],
            })
            return
        if path == "/api/owner/messaging/rooms":
            if not self.owner_allowed():
                self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 열 수 있습니다."}, HTTPStatus.FORBIDDEN)
                return
            try:
                rooms = messaging_connector_rooms()
            except (OSError, RuntimeError, subprocess.TimeoutExpired, urllib.error.URLError, ValueError, json.JSONDecodeError):
                self.send_json({"error": "메시지 연결기에서 카카오톡 채팅방을 불러오지 못했습니다."}, HTTPStatus.BAD_GATEWAY)
                return
            self.send_json({"rooms": rooms})
            return
        if path == "/api/owner/messaging/messages":
            if not self.owner_allowed():
                self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 열 수 있습니다."}, HTTPStatus.FORBIDDEN)
                return
            student_id = query.get("studentId", [""])[0].strip()[:80]
            with db() as connection:
                link = connection.execute(
                    "SELECT chat_id,room_title FROM kakao_parent_rooms WHERE student_id=?", (student_id,)
                ).fetchone()
            if not link:
                self.send_json({"error": "이 학생의 학부모 카톡방을 먼저 연결해 주세요."}, HTTPStatus.CONFLICT)
                return
            try:
                messages = messaging_connector_messages(link["chat_id"])
            except (OSError, RuntimeError, subprocess.TimeoutExpired, urllib.error.URLError, ValueError, json.JSONDecodeError):
                self.send_json({"error": "최근 카카오톡 대화를 확인하지 못했습니다."}, HTTPStatus.BAD_GATEWAY)
                return
            self.send_json({"roomTitle": link["room_title"], "messages": messages})
            return
        if path == "/api/owner/kiosk":
            if not self.owner_allowed():
                self.send_json({"error": "원장 로그인이 필요합니다."}, HTTPStatus.FORBIDDEN)
                return
            with db() as connection:
                devices = connection.execute(
                    "SELECT id,name,active,created_at,last_seen_at FROM kiosk_devices ORDER BY active DESC,last_seen_at DESC"
                ).fetchall()
            self.send_json({
                "devices": [dict(row) for row in devices],
                "connector": messaging_connector_status(),
                "kioskUrl": "/kiosk.html",
            })
            return
        if path == "/api/owner/checkins/report":
            if not self.owner_allowed():
                self.send_json({"error": "원장 로그인이 필요합니다."}, HTTPStatus.FORBIDDEN)
                return
            period = query.get("period", ["week"])[0]
            selected_date = query.get("date", [now_kst().date().isoformat()])[0]
            try:
                with db() as connection:
                    report = build_checkin_report(connection, period, selected_date)
            except ValueError as error:
                self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
                return
            self.send_json(report)
            return
        if path == "/api/owner/student-attendance":
            if not self.owner_allowed():
                self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 열 수 있습니다."}, HTTPStatus.FORBIDDEN)
                return
            student_id = query.get("studentId", [""])[0].strip()[:80]
            with db() as connection:
                clauses = "WHERE student_id=?" if student_id else ""
                parameters = (student_id,) if student_id else ()
                records = connection.execute(
                    f"""
                    SELECT * FROM student_attendance_records {clauses}
                    ORDER BY lesson_date DESC, updated_at DESC
                    """,
                    parameters,
                ).fetchall()
                status_events = connection.execute(
                    """
                    SELECT * FROM student_status_events
                    WHERE student_id=? ORDER BY effective_date DESC,id DESC
                    """,
                    (student_id,),
                ).fetchall() if student_id else []
            counts = {key: 0 for key in STUDENT_ATTENDANCE_LABELS}
            for row in records:
                counts[row["attendance_status"]] += 1
            self.send_json({
                "records": [student_attendance_as_dict(row) for row in records],
                "statusEvents": [dict(row) for row in status_events],
                "summary": {"total": len(records), **counts},
            })
            return
        if path == "/api/owner/teacher-history":
            if not self.owner_allowed():
                self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 열 수 있습니다."}, HTTPStatus.FORBIDDEN)
                return
            academy_teacher_id = query.get("teacherId", [""])[0].strip()[:80]
            if not academy_teacher_id:
                self.send_json({"error": "선생님을 선택해 주세요."}, HTTPStatus.BAD_REQUEST)
                return
            with db() as connection:
                teacher = connection.execute(
                    "SELECT * FROM academy_teachers WHERE id=?", (academy_teacher_id,)
                ).fetchone()
                if not teacher:
                    self.send_json({"error": "선생님 정보를 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
                    return
                requests = connection.execute(
                    """
                    SELECT a.* FROM attendance_requests a
                    JOIN teachers t ON t.id=a.teacher_id
                    WHERE t.academy_teacher_id=?
                    ORDER BY a.work_date DESC,a.requested_at DESC
                    """,
                    (academy_teacher_id,),
                ).fetchall()
                adjustments = connection.execute(
                    """
                    SELECT a.* FROM attendance_adjustment_requests a
                    JOIN teachers t ON t.id=a.teacher_id
                    WHERE t.academy_teacher_id=?
                    ORDER BY a.work_date DESC,a.requested_at DESC
                    """,
                    (academy_teacher_id,),
                ).fetchall()
                work_schedules = connection.execute(
                    """
                    SELECT * FROM teacher_work_schedule WHERE academy_teacher_id=?
                    ORDER BY CASE day WHEN 'mon' THEN 1 WHEN 'tue' THEN 2 WHEN 'wed' THEN 3
                      WHEN 'thu' THEN 4 WHEN 'fri' THEN 5 WHEN 'sat' THEN 6 ELSE 7 END
                    """,
                    (academy_teacher_id,),
                ).fetchall()
                employment_events = connection.execute(
                    """
                    SELECT * FROM teacher_employment_events WHERE academy_teacher_id=?
                    ORDER BY effective_date DESC,id DESC
                    """,
                    (academy_teacher_id,),
                ).fetchall()
            self.send_json({
                "teacher": dict(teacher),
                "requests": [dict(row) for row in requests],
                "adjustments": [dict(row) for row in adjustments],
                "workSchedules": [dict(row) for row in work_schedules],
                "employmentEvents": [dict(row) for row in employment_events],
            })
            return
        if path == "/api/owner/attendance":
            if not self.owner_allowed():
                self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 열 수 있습니다."}, HTTPStatus.FORBIDDEN)
                return
            with db() as connection:
                rows = connection.execute(
                    """
                    SELECT a.*, t.name AS teacher_name
                    FROM attendance_requests a JOIN teachers t ON t.id = a.teacher_id
                    ORDER BY CASE a.status WHEN 'pending' THEN 0 ELSE 1 END, a.requested_at DESC
                    LIMIT 150
                    """
                ).fetchall()
                adjustments = connection.execute(
                    """
                    SELECT a.*, t.name AS teacher_name
                    FROM attendance_adjustment_requests a JOIN teachers t ON t.id=a.teacher_id
                    ORDER BY CASE a.status WHEN 'pending' THEN 0 ELSE 1 END, a.requested_at DESC
                    LIMIT 150
                    """
                ).fetchall()
                teachers = connection.execute(
                    """
                    SELECT a.id AS academy_teacher_id, a.name, a.active, a.subject,
                           a.salary_type, a.salary_amount,a.hire_date,a.termination_date,
                           (SELECT t.id FROM teachers t WHERE t.academy_teacher_id=a.id
                            ORDER BY CASE WHEN t.kakao_id IS NOT NULL THEN 0 ELSE 1 END, t.created_at LIMIT 1) AS id
                    FROM academy_teachers a ORDER BY a.sort_order, a.name
                    """
                ).fetchall()
                work_schedules = connection.execute(
                    """
                    SELECT academy_teacher_id,day,start_time,end_time,break_minutes,note
                    FROM teacher_work_schedule
                    ORDER BY CASE day
                      WHEN 'mon' THEN 1 WHEN 'tue' THEN 2 WHEN 'wed' THEN 3
                      WHEN 'thu' THEN 4 WHEN 'fri' THEN 5 WHEN 'sat' THEN 6 ELSE 7 END
                    """
                ).fetchall()
            self.send_json({
                "requests": [dict(row) for row in rows],
                "adjustments": [dict(row) for row in adjustments],
                "teachers": [dict(row) for row in teachers],
                "workSchedules": [dict(row) for row in work_schedules],
            })
            return
        if path == "/api/owner/state":
            if not self.owner_allowed():
                self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 열 수 있습니다."}, HTTPStatus.FORBIDDEN)
                return
            with db() as connection:
                initialized = owner_state_initialized(connection)
                state = serialize_owner_state(connection) if initialized else None
            self.send_json({"initialized": initialized, "state": state})
            return
        if path == "/auth/demo":
            if os.environ.get("KAKAO_REST_API_KEY") and os.environ.get("ACADEMY_ENABLE_DEMO_LOGIN") != "1":
                self.send_json({"error": "운영 환경에서는 체험 로그인을 사용할 수 없습니다."}, HTTPStatus.NOT_FOUND)
                return
            teacher_id = query.get("teacher", ["demo1"])[0]
            if teacher_id not in {"demo1", "demo2"}:
                teacher_id = "demo1"
            token = make_session(teacher_id)
            cookie = self.teacher_cookie(token)
            self.send_redirect("/teacher.html", cookie)
            return
        if path == "/auth/kakao/start":
            rest_key = os.environ.get("KAKAO_REST_API_KEY")
            if not rest_key:
                self.send_redirect("/teacher.html?error=kakao_not_configured")
                return
            state = secrets.token_urlsafe(24)
            OAUTH_STATES[state] = time.time()
            redirect_uri = os.environ.get("KAKAO_REDIRECT_URI", "http://127.0.0.1:49321/auth/kakao/callback")
            params = urllib.parse.urlencode({
                "response_type": "code",
                "client_id": rest_key,
                "redirect_uri": redirect_uri,
                "state": state,
            })
            self.send_redirect(f"https://kauth.kakao.com/oauth/authorize?{params}")
            return
        if path == "/auth/kakao/callback":
            self.handle_kakao_callback(query)
            return
        if path == "/auth/logout":
            token = self.cookies().get(SESSION_COOKIE)
            if token:
                with db() as connection:
                    connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash(token),))
            cookie = self.teacher_cookie("", 0)
            self.send_redirect("/teacher.html", cookie)
            return
        super().do_GET()

    def handle_kakao_callback(self, query):
        state = query.get("state", [""])[0]
        created = OAUTH_STATES.pop(state, None)
        if not created or time.time() - created > 600:
            self.send_redirect("/teacher.html?error=invalid_state")
            return
        code = query.get("code", [""])[0]
        if not code:
            self.send_redirect("/teacher.html?error=login_cancelled")
            return
        rest_key = os.environ.get("KAKAO_REST_API_KEY", "")
        redirect_uri = os.environ.get("KAKAO_REDIRECT_URI", "http://127.0.0.1:49321/auth/kakao/callback")
        token_params = {
            "grant_type": "authorization_code",
            "client_id": rest_key,
            "redirect_uri": redirect_uri,
            "code": code,
        }
        if os.environ.get("KAKAO_CLIENT_SECRET"):
            token_params["client_secret"] = os.environ["KAKAO_CLIENT_SECRET"]
        try:
            token_req = urllib.request.Request(
                "https://kauth.kakao.com/oauth/token",
                data=urllib.parse.urlencode(token_params).encode("utf-8"),
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            )
            with urllib.request.urlopen(token_req, timeout=15) as response:
                token_data = json.load(response)
            access_token = token_data["access_token"]
            user_req = urllib.request.Request(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            with urllib.request.urlopen(user_req, timeout=15) as response:
                user_data = json.load(response)
        except (urllib.error.URLError, KeyError, ValueError):
            self.send_redirect("/teacher.html?error=kakao_exchange_failed")
            return

        kakao_id = str(user_data["id"])
        props = user_data.get("properties") or {}
        account = user_data.get("kakao_account") or {}
        profile = account.get("profile") or {}
        name = props.get("nickname") or profile.get("nickname") or f"선생님 {kakao_id[-4:]}"
        image = props.get("profile_image") or profile.get("profile_image_url")
        phone = normalize_phone(account.get("phone_number"))
        with db() as connection:
            existing = connection.execute("SELECT id FROM teachers WHERE kakao_id = ?", (kakao_id,)).fetchone()
            if not existing and phone:
                phone_matches = [
                    row
                    for row in connection.execute(
                        """
                        SELECT t.id, a.phone FROM teachers t
                        JOIN academy_teachers a ON a.id=t.academy_teacher_id
                        WHERE t.kakao_id IS NULL AND t.active=1 AND a.active=1
                        """
                    )
                    if normalize_phone(row["phone"]) == phone
                ]
                if len(phone_matches) == 1:
                    existing = phone_matches[0]
            if not existing:
                existing = connection.execute(
                    "SELECT id FROM teachers WHERE name = ? AND kakao_id IS NULL ORDER BY created_at LIMIT 1",
                    (name,),
                ).fetchone()
            if existing:
                teacher_id = existing["id"]
                connection.execute(
                    "UPDATE teachers SET kakao_id=?, name=?, profile_image=? WHERE id=?",
                    (kakao_id, name, image, teacher_id),
                )
            else:
                teacher_id = f"kakao:{kakao_id}"
                connection.execute(
                    "INSERT INTO teachers(id, kakao_id, name, profile_image, created_at) VALUES (?, ?, ?, ?, ?)",
                    (teacher_id, kakao_id, name, image, iso_now()),
                )
        token = make_session(teacher_id)
        cookie = self.teacher_cookie(token)
        self.send_redirect("/teacher.html", cookie)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/kiosk/pair":
            self.pair_kiosk()
            return
        if path == "/api/kiosk/checkin":
            self.create_student_checkin()
            return
        if path == "/api/owner/login":
            self.owner_login()
            return
        if path == "/api/owner/logout":
            self.owner_logout()
            return
        if path == "/api/owner/photos":
            self.receive_photos()
            return
        if path == "/api/teacher/attendance":
            self.create_attendance_request()
            return
        if path == "/api/teacher/attendance-adjustment":
            self.create_attendance_adjustment()
            return
        if path == "/api/teacher/evaluations":
            self.save_student_evaluation()
            return
        if path == "/api/teacher/student-attendance":
            self.save_student_attendance()
            return
        if path == "/api/owner/work-schedule":
            self.save_teacher_work_schedule()
            return
        if path == "/api/owner/teacher-absence":
            self.save_teacher_absence()
            return
        if path == "/api/owner/schedule":
            self.replace_schedule()
            return
        if path == "/api/owner/state":
            self.save_owner_state()
            return
        if path == "/api/owner/messaging/link":
            self.save_messaging_link()
            return
        if path == "/api/owner/kiosk/pairing-code":
            self.issue_kiosk_pairing_code()
            return
        if path == "/api/owner/kiosk/device-status":
            self.update_kiosk_device_status()
            return
        if path == "/api/owner/checkins/report/send":
            self.send_checkin_report_to_kakao()
            return
        if path.startswith("/api/owner/evaluations/") and path.endswith("/kakao-send"):
            self.send_evaluation_to_kakao(path)
            return
        if path.startswith("/api/owner/attendance/"):
            self.review_attendance(path)
            return
        if path.startswith("/api/owner/adjustments/"):
            self.review_attendance_adjustment(path)
            return
        if path.startswith("/api/owner/evaluations/"):
            self.update_evaluation_message(path)
            return
        self.send_json({"error": "지원하지 않는 요청입니다."}, HTTPStatus.NOT_FOUND)

    def issue_kiosk_pairing_code(self):
        if not self.owner_allowed():
            self.send_json({"error": "원장 로그인이 필요합니다."}, HTTPStatus.FORBIDDEN)
            return
        try:
            with db() as connection:
                pairing = create_kiosk_pairing_code(connection)
        except RuntimeError as error:
            self.send_json({"error": str(error)}, HTTPStatus.SERVICE_UNAVAILABLE)
            return
        self.send_json({"ok": True, **pairing})

    def pair_kiosk(self):
        address = self.client_address[0]
        if limited_attempt(KIOSK_PAIR_ATTEMPTS, address, 8, 600):
            self.send_json({"error": "연결 시도가 많습니다. 10분 뒤 다시 시도해 주세요."}, HTTPStatus.TOO_MANY_REQUESTS)
            return
        try:
            payload = self.read_json()
            with db() as connection:
                result = pair_kiosk_device(connection, payload.get("code", ""), payload.get("deviceName", ""))
        except (ValueError, json.JSONDecodeError) as error:
            note_failed_attempt(KIOSK_PAIR_ATTEMPTS, address)
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        KIOSK_PAIR_ATTEMPTS.pop(address, None)
        self.send_json({"ok": True, **result}, HTTPStatus.CREATED)

    def create_student_checkin(self):
        token = kiosk_bearer_token(self.headers)
        device = kiosk_device_for_token(token)
        if not device:
            self.send_json({"error": "등원 기기 연결이 필요합니다.", "pairingRequired": True}, HTTPStatus.UNAUTHORIZED)
            return
        attempt_key = device["id"]
        if limited_attempt(KIOSK_CHECKIN_ATTEMPTS, attempt_key, 15, 300):
            self.send_json({"error": "번호 확인이 반복되었습니다. 잠시 뒤 다시 시도해 주세요."}, HTTPStatus.TOO_MANY_REQUESTS)
            return
        try:
            payload = self.read_json()
            with db() as connection:
                result = record_student_checkin(
                    connection, payload.get("code", ""), device["id"],
                    selected_student_id=str(payload.get("studentId", ""))[:80],
                )
        except (ValueError, LookupError, RuntimeError, json.JSONDecodeError) as error:
            note_failed_attempt(KIOSK_CHECKIN_ATTEMPTS, attempt_key)
            self.send_json({"error": str(error)}, HTTPStatus.CONFLICT if isinstance(error, RuntimeError) else HTTPStatus.BAD_REQUEST)
            return
        if result.get("selectionRequired"):
            self.send_json({"ok": True, **result})
            return
        KIOSK_CHECKIN_ATTEMPTS.pop(attempt_key, None)
        if not result["duplicate"]:
            threading.Thread(
                target=deliver_checkin_notification,
                args=(result["id"],),
                name=f"checkin-notify-{result['id']}",
                daemon=True,
            ).start()
        self.send_json({
            "ok": True,
            **result,
            "notice": (
                f"{result['studentName']} 학생은 조금 전에 이미 등원했습니다."
                if result["duplicate"] else f"{result['studentName']} 학생, 등원 확인되었습니다."
            ),
            "notificationQueued": not result["duplicate"],
        }, HTTPStatus.OK if result["duplicate"] else HTTPStatus.CREATED)

    def update_kiosk_device_status(self):
        if not self.owner_allowed():
            self.send_json({"error": "원장 로그인이 필요합니다."}, HTTPStatus.FORBIDDEN)
            return
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        device_id = str(payload.get("deviceId", "")).strip()[:80]
        active = 1 if payload.get("active") is True else 0
        with db() as connection:
            result = connection.execute(
                "UPDATE kiosk_devices SET active=? WHERE id=?", (active, device_id)
            )
        if not result.rowcount:
            self.send_json({"error": "등원 기기를 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
            return
        self.send_json({"ok": True, "active": bool(active)})

    def send_checkin_report_to_kakao(self):
        if not self.owner_allowed():
            self.send_json({"error": "원장 로그인이 필요합니다."}, HTTPStatus.FORBIDDEN)
            return
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        if payload.get("confirmed") is not True:
            self.send_json({"error": "받는 카톡방과 리포트 문안을 확인한 뒤 전송해 주세요."}, HTTPStatus.BAD_REQUEST)
            return
        student_id = str(payload.get("studentId", "")).strip()[:80]
        message = str(payload.get("message", "")).strip()[:6000]
        request_id = str(payload.get("requestId", "")).strip()[:100]
        period_key = str(payload.get("periodKey", "")).strip()[:100]
        if not student_id or len(message) < 5 or len(request_id) < 8 or not period_key:
            self.send_json({"error": "리포트 전송 정보가 올바르지 않습니다."}, HTTPStatus.BAD_REQUEST)
            return
        with db() as connection:
            link = connection.execute(
                "SELECT chat_id,room_title FROM kakao_parent_rooms WHERE student_id=?", (student_id,)
            ).fetchone()
            existing = connection.execute(
                "SELECT status FROM kakao_send_log WHERE id=?", (request_id,)
            ).fetchone()
        if not link:
            self.send_json({"error": "이 학생의 학부모 카톡방을 먼저 연결해 주세요."}, HTTPStatus.CONFLICT)
            return
        if existing:
            self.send_json({"ok": existing["status"] == "sent", "status": existing["status"], "notice": "이미 처리한 전송 요청입니다."})
            return
        if not KAKAO_SEND_LOCK.acquire(blocking=False):
            self.send_json({"error": "다른 카톡을 전송 중입니다. 잠시 뒤 다시 눌러 주세요."}, HTTPStatus.CONFLICT)
            return
        attempted_at = iso_now()
        try:
            with db() as connection:
                connection.execute(
                    """
                    INSERT INTO kakao_send_log(
                      id,evaluation_id,student_id,chat_id,room_title,message,status,attempted_at
                    ) VALUES (?,?,?,?,?,?,?,?)
                    """,
                    (request_id, f"checkin-report:{student_id}:{period_key}", student_id, link["chat_id"], link["room_title"], message, "sending", attempted_at),
                )
            try:
                sent = messaging_connector_send(link["chat_id"], message)
            except (OSError, RuntimeError, subprocess.TimeoutExpired, urllib.error.URLError, ValueError, json.JSONDecodeError):
                sent = False
            status = "sent" if sent else "unknown"
            with db() as connection:
                connection.execute(
                    "UPDATE kakao_send_log SET status=?,finished_at=? WHERE id=?",
                    (status, iso_now(), request_id),
                )
            self.send_json({
                "ok": sent, "status": status,
                "notice": "등원 리포트를 전송했습니다." if sent else "전송 결과를 확인하지 못했습니다. 자동으로 다시 보내지 않습니다.",
            })
        finally:
            KAKAO_SEND_LOCK.release()

    def save_messaging_link(self):
        if not self.owner_allowed():
            self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 사용할 수 있습니다."}, HTTPStatus.FORBIDDEN)
            return
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        student_id = str(payload.get("studentId", "")).strip()[:80]
        chat_id = str(payload.get("chatId", "")).strip()[:500]
        if not student_id or not chat_id:
            self.send_json({"error": "학생과 학부모 카톡방을 선택해 주세요."}, HTTPStatus.BAD_REQUEST)
            return
        with db() as connection:
            student = connection.execute(
                "SELECT id,name FROM academy_students WHERE id=?", (student_id,)
            ).fetchone()
        if not student:
            self.send_json({"error": "학생 정보를 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
            return
        try:
            matches = [room for room in messaging_connector_rooms() if room["chatId"] == chat_id]
        except (OSError, RuntimeError, subprocess.TimeoutExpired, urllib.error.URLError, ValueError, json.JSONDecodeError):
            self.send_json({"error": "메시지 연결기에서 선택한 카톡방을 확인하지 못했습니다."}, HTTPStatus.BAD_GATEWAY)
            return
        if len(matches) != 1:
            self.send_json({"error": "정확한 카톡방을 확인할 수 없습니다. 채팅방 목록을 다시 불러와 주세요."}, HTTPStatus.CONFLICT)
            return
        timestamp = iso_now()
        with db() as connection:
            connection.execute(
                """
                INSERT INTO kakao_parent_rooms(student_id,chat_id,room_title,linked_at,updated_at)
                VALUES (?,?,?,?,?)
                ON CONFLICT(student_id) DO UPDATE SET
                  chat_id=excluded.chat_id,room_title=excluded.room_title,updated_at=excluded.updated_at
                """,
                (student_id, chat_id, matches[0]["title"], timestamp, timestamp),
            )
        self.send_json({
            "ok": True,
            "notice": f"{student['name']} 학생과 선택한 학부모 카톡방을 연결했습니다.",
            "link": {"studentId": student_id, "roomTitle": matches[0]["title"]},
        })

    def send_evaluation_to_kakao(self, path):
        if not self.owner_allowed():
            self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 사용할 수 있습니다."}, HTTPStatus.FORBIDDEN)
            return
        parts = path.strip("/").split("/")
        if len(parts) != 5 or parts[:3] != ["api", "owner", "evaluations"] or parts[4] != "kakao-send":
            self.send_json({"error": "잘못된 카톡 발송 요청입니다."}, HTTPStatus.BAD_REQUEST)
            return
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        if payload.get("confirmed") is not True:
            self.send_json({"error": "받는 카톡방과 문안을 확인한 뒤 전송해 주세요."}, HTTPStatus.BAD_REQUEST)
            return
        evaluation_id = parts[3][:80]
        message = str(payload.get("message", "")).strip()[:6000]
        request_id = str(payload.get("requestId", "")).strip()[:100]
        if len(message) < 5 or len(request_id) < 8:
            self.send_json({"error": "보낼 문안 또는 전송 요청 정보가 올바르지 않습니다."}, HTTPStatus.BAD_REQUEST)
            return
        with db() as connection:
            row = connection.execute(
                """
                SELECT e.*,r.chat_id,r.room_title
                FROM student_evaluations e
                LEFT JOIN kakao_parent_rooms r ON r.student_id=e.student_id
                WHERE e.id=?
                """,
                (evaluation_id,),
            ).fetchone()
            if not row:
                self.send_json({"error": "학생 평가를 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
                return
            if not row["chat_id"]:
                self.send_json({"error": "이 학생의 학부모 카톡방을 먼저 연결해 주세요."}, HTTPStatus.CONFLICT)
                return
            existing = connection.execute(
                "SELECT status FROM kakao_send_log WHERE id=?", (request_id,)
            ).fetchone()
            if existing:
                self.send_json({
                    "ok": existing["status"] == "sent",
                    "status": existing["status"],
                    "notice": "이미 처리한 전송 요청입니다. 카카오톡에서 결과를 확인해 주세요.",
                })
                return
        if not KAKAO_SEND_LOCK.acquire(blocking=False):
            self.send_json({"error": "다른 카톡을 전송 중입니다. 잠시 뒤 다시 눌러 주세요."}, HTTPStatus.CONFLICT)
            return
        attempted_at = iso_now()
        try:
            with db() as connection:
                connection.execute(
                    """
                    INSERT INTO kakao_send_log(
                      id,evaluation_id,student_id,chat_id,room_title,message,status,attempted_at
                    ) VALUES (?,?,?,?,?,?,?,?)
                    """,
                    (
                        request_id, evaluation_id, row["student_id"], row["chat_id"],
                        row["room_title"], message, "sending", attempted_at,
                    ),
                )
            sent = False
            try:
                sent = messaging_connector_send(row["chat_id"], message)
            except (OSError, RuntimeError, subprocess.TimeoutExpired, urllib.error.URLError, ValueError, json.JSONDecodeError):
                sent = False
            status = "sent" if sent else "unknown"
            finished_at = iso_now()
            with db() as connection:
                connection.execute(
                    "UPDATE kakao_send_log SET status=?,finished_at=? WHERE id=?",
                    (status, finished_at, request_id),
                )
                if sent:
                    connection.execute(
                        """
                        UPDATE student_evaluations
                        SET message_draft=?,message_status='sent',message_updated_at=?,sent_at=?
                        WHERE id=?
                        """,
                        (message, finished_at, finished_at, evaluation_id),
                    )
            self.send_json({
                "ok": sent,
                "status": status,
                "notice": (
                    "카톡 전송을 완료로 기록했습니다. 상대방의 수신·읽음 여부는 카카오톡에서 확인해 주세요."
                    if sent else
                    "전송 결과를 확인하지 못했습니다. 카카오톡에서 확인해 주세요. 자동으로 다시 보내지 않습니다."
                ),
            })
        finally:
            KAKAO_SEND_LOCK.release()

    def owner_login(self):
        if not owner_is_configured():
            self.send_json({"error": "원장 계정이 아직 설정되지 않았습니다."}, HTTPStatus.CONFLICT)
            return
        now = time.time()
        address = self.client_address[0]
        attempts = [stamp for stamp in OWNER_LOGIN_ATTEMPTS.get(address, []) if now - stamp < 600]
        if len(attempts) >= 8:
            self.send_json({"error": "로그인 시도가 많습니다. 10분 뒤 다시 시도해 주세요."}, HTTPStatus.TOO_MANY_REQUESTS)
            return
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        username = str(payload.get("username", "owner")).strip()[:80]
        password = str(payload.get("password", ""))
        if not verify_owner_password(username, password):
            attempts.append(now)
            OWNER_LOGIN_ATTEMPTS[address] = attempts
            self.send_json({"error": "아이디 또는 비밀번호가 올바르지 않습니다."}, HTTPStatus.UNAUTHORIZED)
            return
        OWNER_LOGIN_ATTEMPTS.pop(address, None)
        token = make_owner_session(username)
        self.send_json_with_cookie(
            {"ok": True, "redirect": "/"},
            self.owner_cookie(token),
        )

    def owner_logout(self):
        token = self.cookies().get(OWNER_SESSION_COOKIE)
        if token:
            with db() as connection:
                connection.execute("DELETE FROM owner_sessions WHERE token_hash=?", (token_hash(token),))
        self.send_json_with_cookie(
            {"ok": True, "redirect": "/owner-login.html"},
            self.owner_cookie("", 0),
        )

    def save_owner_state(self):
        if not self.owner_allowed():
            self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 사용할 수 있습니다."}, HTTPStatus.FORBIDDEN)
            return
        try:
            payload = self.read_json()
            state = payload.get("state")
            with db() as connection:
                replace_owner_state(connection, state)
        except (ValueError, TypeError, json.JSONDecodeError, sqlite3.IntegrityError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"ok": True, "savedAt": iso_now()})

    def replace_schedule(self):
        if not self.owner_allowed():
            self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 사용할 수 있습니다."}, HTTPStatus.FORBIDDEN)
            return
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        lessons = payload.get("lessons")
        if not isinstance(lessons, list) or len(lessons) > 300:
            self.send_json({"error": "시간표 형식이 올바르지 않습니다."}, HTTPStatus.BAD_REQUEST)
            return
        cleaned = []
        for item in lessons:
            if not isinstance(item, dict):
                self.send_json({"error": "수업 정보 형식이 올바르지 않습니다."}, HTTPStatus.BAD_REQUEST)
                return
            lesson_id = str(item.get("id", ""))[:80]
            day = str(item.get("day", ""))
            class_name = str(item.get("className", "")).strip()[:120]
            subject = str(item.get("subject", "")).strip()[:120]
            if not lesson_id or day not in SCHEDULE_DAYS or not class_name or not subject:
                self.send_json({"error": "수업의 요일·반·과목 정보가 필요합니다."}, HTTPStatus.BAD_REQUEST)
                return
            students = item.get("students") or []
            if not isinstance(students, list) or len(students) > 100:
                self.send_json({"error": "학생 명단 형식이 올바르지 않습니다."}, HTTPStatus.BAD_REQUEST)
                return
            cleaned_students = []
            for student in students:
                if not isinstance(student, dict) or not str(student.get("name", "")).strip():
                    self.send_json({"error": "학생 이름이 필요합니다."}, HTTPStatus.BAD_REQUEST)
                    return
                cleaned_students.append({
                    "id": str(student.get("id", ""))[:80],
                    "name": str(student.get("name", "")).strip()[:80],
                    "school": str(student.get("school", "")).strip()[:120],
                })
            cleaned.append((
                lesson_id,
                day,
                str(item.get("start", ""))[:10],
                str(item.get("end", ""))[:10],
                str(item.get("timeLabel", ""))[:40],
                class_name,
                subject,
                str(item.get("teacherName", "")).strip()[:100],
                json.dumps(cleaned_students, ensure_ascii=False),
                iso_now(),
                str(item.get("teacherId", "")).strip()[:80] or None,
                json.dumps([student["id"] for student in cleaned_students if student["id"]], ensure_ascii=False),
            ))
        with db() as connection:
            connection.execute("DELETE FROM class_schedule")
            connection.executemany(
                """
                INSERT INTO class_schedule(
                  id, day, start_time, end_time, time_label, class_name,
                  subject, teacher_name, students_json, updated_at, teacher_id, student_ids_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                cleaned,
            )
        self.send_json({"ok": True, "count": len(cleaned)})

    def save_teacher_work_schedule(self):
        if not self.owner_allowed():
            self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 사용할 수 있습니다."}, HTTPStatus.FORBIDDEN)
            return
        try:
            payload = self.read_json()
            academy_teacher_id = str(payload.get("academyTeacherId", "")).strip()[:80]
            schedule = payload.get("schedule")
            if not academy_teacher_id:
                raise ValueError("선생님을 선택해 주세요.")
            with db() as connection:
                replace_teacher_work_schedule(connection, academy_teacher_id, schedule)
        except (ValueError, TypeError, json.JSONDecodeError, sqlite3.IntegrityError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"ok": True, "count": len(schedule), "savedAt": iso_now()})

    def save_teacher_absence(self):
        if not self.owner_allowed():
            self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 사용할 수 있습니다."}, HTTPStatus.FORBIDDEN)
            return
        try:
            payload = self.read_json()
            academy_teacher_id = str(payload.get("academyTeacherId", "")).strip()[:80]
            work_date = str(payload.get("workDate", "")).strip()[:10]
            reason = str(payload.get("reason", "")).strip()[:1000]
            if not academy_teacher_id:
                raise ValueError("선생님을 선택해 주세요.")
            with db() as connection:
                record_id = record_teacher_absence(
                    connection, academy_teacher_id, work_date, reason
                )
        except (ValueError, TypeError, json.JSONDecodeError, sqlite3.IntegrityError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"ok": True, "recordId": record_id, "savedAt": iso_now()}, HTTPStatus.CREATED)

    def save_student_evaluation(self):
        teacher = self.current_teacher()
        if not teacher:
            self.send_json({"error": "로그인이 필요합니다."}, HTTPStatus.UNAUTHORIZED)
            return
        try:
            payload = self.read_json()
            lesson_id = text_value(payload, "lessonId", 80)
            student_id = text_value(payload, "studentId", 80)
            lesson_date = text_value(payload, "lessonDate", 10)
            note = text_value(payload, "note", 2000)
            if not lesson_id or not student_id:
                raise ValueError("수업과 학생을 선택해 주세요.")
            try:
                parsed_date = datetime.strptime(lesson_date, "%Y-%m-%d").date()
            except ValueError as error:
                raise ValueError("수업일을 올바르게 선택해 주세요.") from error
            if parsed_date > now_kst().date():
                raise ValueError("아직 진행하지 않은 수업은 평가할 수 없습니다.")
            if len(note) < 2:
                raise ValueError("선생님 관찰 내용을 한 문장 이상 적어 주세요.")
            scores = {}
            for field in EVALUATION_FIELDS:
                try:
                    score = int(payload.get(field, 0))
                except (TypeError, ValueError) as error:
                    raise ValueError("모든 평가 항목을 선택해 주세요.") from error
                if score not in {1, 2, 3, 4}:
                    raise ValueError("모든 평가 항목을 선택해 주세요.")
                scores[field] = score
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return

        with db() as connection:
            lesson = connection.execute(
                """
                SELECT * FROM class_schedule
                WHERE id=? AND (
                  teacher_id=COALESCE(?, '') OR
                  (COALESCE(teacher_id, '')='' AND teacher_name=?)
                )
                """,
                (lesson_id, teacher["academy_teacher_id"], teacher["name"]),
            ).fetchone()
            if not lesson:
                self.send_json({"error": "담당 수업을 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
                return
            if lesson["day"] != day_key_for_date(lesson_date):
                self.send_json({"error": "선택한 날짜에는 이 수업이 없습니다."}, HTTPStatus.CONFLICT)
                return
            student = next(
                (
                    item for item in json_list(lesson["students_json"])
                    if str(item.get("id", "")) == student_id
                ),
                None,
            )
            if not student:
                self.send_json({"error": "이 수업에 등록된 학생이 아닙니다."}, HTTPStatus.CONFLICT)
                return
            timestamp = iso_now()
            evaluation_id = f"eval-{secrets.token_hex(12)}"
            connection.execute(
                """
                INSERT INTO student_evaluations(
                  id,lesson_id,lesson_date,teacher_id,academy_teacher_id,teacher_name,
                  student_id,student_name,class_name,subject,attitude,concentration,
                  understanding,progress,participation,homework,note,created_at,updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(lesson_id,lesson_date,student_id) DO UPDATE SET
                  teacher_id=excluded.teacher_id,
                  academy_teacher_id=excluded.academy_teacher_id,
                  teacher_name=excluded.teacher_name,
                  student_name=excluded.student_name,
                  class_name=excluded.class_name,
                  subject=excluded.subject,
                  attitude=excluded.attitude,
                  concentration=excluded.concentration,
                  understanding=excluded.understanding,
                  progress=excluded.progress,
                  participation=excluded.participation,
                  homework=excluded.homework,
                  note=excluded.note,
                  message_status=CASE
                    WHEN student_evaluations.message_status='sent' THEN 'updated_after_sent'
                    ELSE 'pending'
                  END,
                  updated_at=excluded.updated_at
                """,
                (
                    evaluation_id, lesson_id, lesson_date, teacher["id"],
                    teacher["academy_teacher_id"] or "", teacher["name"], student_id,
                    str(student.get("name", "학생"))[:100], lesson["class_name"], lesson["subject"],
                    scores["attitude"], scores["concentration"], scores["understanding"],
                    scores["progress"], scores["participation"], scores["homework"], note,
                    timestamp, timestamp,
                ),
            )
            saved = connection.execute(
                """
                SELECT * FROM student_evaluations
                WHERE lesson_id=? AND lesson_date=? AND student_id=?
                """,
                (lesson_id, lesson_date, student_id),
            ).fetchone()
            connection.execute(
                """
                INSERT OR IGNORE INTO student_attendance_records(
                  lesson_id,lesson_date,teacher_id,academy_teacher_id,teacher_name,
                  student_id,student_name,class_name,subject,attendance_status,note,
                  recorded_at,updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,'present','',?,?)
                """,
                (
                    lesson_id, lesson_date, teacher["id"], teacher["academy_teacher_id"] or "",
                    teacher["name"], student_id, str(student.get("name", "학생"))[:100],
                    lesson["class_name"], lesson["subject"], timestamp, timestamp,
                ),
            )
        self.send_json({"ok": True, "evaluation": evaluation_as_dict(saved)}, HTTPStatus.CREATED)

    def save_student_attendance(self):
        teacher = self.current_teacher()
        if not teacher:
            self.send_json({"error": "로그인이 필요합니다."}, HTTPStatus.UNAUTHORIZED)
            return
        try:
            payload = self.read_json()
            lesson_id = text_value(payload, "lessonId", 80)
            student_id = text_value(payload, "studentId", 80)
            lesson_date = text_value(payload, "lessonDate", 10)
            attendance_status = text_value(payload, "attendanceStatus", 20)
            note = text_value(payload, "note", 1000)
            if not lesson_id or not student_id:
                raise ValueError("수업과 학생을 선택해 주세요.")
            if attendance_status not in STUDENT_ATTENDANCE_LABELS:
                raise ValueError("출결 상태를 올바르게 선택해 주세요.")
            try:
                parsed_date = datetime.strptime(lesson_date, "%Y-%m-%d").date()
            except ValueError as error:
                raise ValueError("수업일을 올바르게 선택해 주세요.") from error
            if parsed_date > now_kst().date():
                raise ValueError("아직 진행하지 않은 수업의 출결은 기록할 수 없습니다.")
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return

        with db() as connection:
            lesson = connection.execute(
                """
                SELECT * FROM class_schedule
                WHERE id=? AND (
                  teacher_id=COALESCE(?, '') OR
                  (COALESCE(teacher_id, '')='' AND teacher_name=?)
                )
                """,
                (lesson_id, teacher["academy_teacher_id"], teacher["name"]),
            ).fetchone()
            if not lesson:
                self.send_json({"error": "담당 수업을 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
                return
            if lesson["day"] != day_key_for_date(lesson_date):
                self.send_json({"error": "선택한 날짜에는 이 수업이 없습니다."}, HTTPStatus.CONFLICT)
                return
            student = next(
                (
                    item for item in json_list(lesson["students_json"])
                    if str(item.get("id", "")) == student_id
                ),
                None,
            )
            if not student:
                self.send_json({"error": "이 수업에 등록된 학생이 아닙니다."}, HTTPStatus.CONFLICT)
                return
            timestamp = iso_now()
            connection.execute(
                """
                INSERT INTO student_attendance_records(
                  lesson_id,lesson_date,teacher_id,academy_teacher_id,teacher_name,
                  student_id,student_name,class_name,subject,attendance_status,note,
                  recorded_at,updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(lesson_id,lesson_date,student_id) DO UPDATE SET
                  teacher_id=excluded.teacher_id,
                  academy_teacher_id=excluded.academy_teacher_id,
                  teacher_name=excluded.teacher_name,
                  student_name=excluded.student_name,
                  class_name=excluded.class_name,
                  subject=excluded.subject,
                  attendance_status=excluded.attendance_status,
                  note=excluded.note,
                  updated_at=excluded.updated_at
                """,
                (
                    lesson_id, lesson_date, teacher["id"], teacher["academy_teacher_id"] or "",
                    teacher["name"], student_id, str(student.get("name", "학생"))[:100],
                    lesson["class_name"], lesson["subject"], attendance_status, note,
                    timestamp, timestamp,
                ),
            )
            saved = connection.execute(
                """
                SELECT * FROM student_attendance_records
                WHERE lesson_id=? AND lesson_date=? AND student_id=?
                """,
                (lesson_id, lesson_date, student_id),
            ).fetchone()
        self.send_json({"ok": True, "attendance": student_attendance_as_dict(saved)}, HTTPStatus.CREATED)

    def update_evaluation_message(self, path):
        if not self.owner_allowed():
            self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 열 수 있습니다."}, HTTPStatus.FORBIDDEN)
            return
        parts = path.strip("/").split("/")
        if len(parts) != 5 or parts[:3] != ["api", "owner", "evaluations"] or parts[4] not in {"draft", "message", "sent"}:
            self.send_json({"error": "잘못된 피드백 요청입니다."}, HTTPStatus.BAD_REQUEST)
            return
        evaluation_id = parts[3][:80]
        action = parts[4]
        with db() as connection:
            row = connection.execute(
                "SELECT * FROM student_evaluations WHERE id=?", (evaluation_id,)
            ).fetchone()
            if not row:
                self.send_json({"error": "학생 평가를 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
                return
            timestamp = iso_now()
            notice = ""
            if action == "draft":
                message, provider, notice = generate_feedback_message(row)
                connection.execute(
                    """
                    UPDATE student_evaluations
                    SET message_draft=?,message_status='draft',message_provider=?,
                        message_updated_at=?,sent_at=NULL
                    WHERE id=?
                    """,
                    (message, provider, timestamp, evaluation_id),
                )
            elif action == "message":
                try:
                    payload = self.read_json()
                except (ValueError, json.JSONDecodeError) as error:
                    self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
                    return
                message = str(payload.get("message", "")).strip()[:6000]
                if len(message) < 5:
                    self.send_json({"error": "학부모에게 보낼 문안을 입력해 주세요."}, HTTPStatus.BAD_REQUEST)
                    return
                connection.execute(
                    """
                    UPDATE student_evaluations
                    SET message_draft=?,message_status='draft',message_updated_at=?,sent_at=NULL
                    WHERE id=?
                    """,
                    (message, timestamp, evaluation_id),
                )
                notice = "원장님 수정 문안을 저장했습니다."
            else:
                if not row["message_draft"].strip():
                    self.send_json({"error": "먼저 학부모 피드백 문안을 만들어 주세요."}, HTTPStatus.CONFLICT)
                    return
                connection.execute(
                    """
                    UPDATE student_evaluations
                    SET message_status='sent',message_updated_at=?,sent_at=? WHERE id=?
                    """,
                    (timestamp, timestamp, evaluation_id),
                )
                notice = "발송 완료로 기록했습니다."
            saved = connection.execute(
                "SELECT * FROM student_evaluations WHERE id=?", (evaluation_id,)
            ).fetchone()
        self.send_json({"ok": True, "notice": notice, "evaluation": evaluation_as_dict(saved)})

    def create_attendance_adjustment(self):
        teacher = self.current_teacher()
        if not teacher:
            self.send_json({"error": "로그인이 필요합니다."}, HTTPStatus.UNAUTHORIZED)
            return
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        request_type = str(payload.get("requestType", ""))
        if request_type not in {"early_leave", "overtime", "schedule_change"}:
            self.send_json({"error": "조퇴·추가근무·근무시간 변경 요청만 가능합니다."}, HTTPStatus.BAD_REQUEST)
            return
        reason = str(payload.get("reason", "")).strip()[:1000]
        if len(reason) < 2:
            self.send_json({"error": "요청 사유를 입력해 주세요."}, HTTPStatus.BAD_REQUEST)
            return
        today_date = now_kst().date()
        today = today_date.isoformat()
        work_date = str(payload.get("workDate", today))[:10] if request_type == "schedule_change" else today
        if request_type == "schedule_change":
            try:
                parsed_work_date = datetime.strptime(work_date, "%Y-%m-%d").date()
            except ValueError:
                self.send_json({"error": "요청할 근무일을 올바르게 선택해 주세요."}, HTTPStatus.BAD_REQUEST)
                return
            days_ahead = (parsed_work_date - today_date).days
            if days_ahead < 0:
                self.send_json({"error": "지난 근무일은 요청할 수 없습니다."}, HTTPStatus.BAD_REQUEST)
                return
        day = day_key_for_date(work_date)
        with db() as connection:
            if request_type != "schedule_change":
                clock_in = connection.execute(
                    """
                    SELECT id FROM attendance_requests
                    WHERE teacher_id=? AND work_date=? AND event_type='clock_in' AND status='approved'
                    """,
                    (teacher["id"], today),
                ).fetchone()
                if not clock_in:
                    self.send_json({"error": "출근이 승인된 뒤 요청할 수 있습니다."}, HTTPStatus.CONFLICT)
                    return
            plan = connection.execute(
                """
                SELECT start_time,end_time FROM teacher_work_schedule
                WHERE academy_teacher_id=? AND day=?
                """,
                (teacher["academy_teacher_id"] or "", day),
            ).fetchone()
            if not plan:
                self.send_json({"error": "선택한 날의 근무시간이 등록되지 않았습니다. 원장님께 먼저 등록을 요청해 주세요."}, HTTPStatus.CONFLICT)
                return
            duplicate = connection.execute(
                """
                SELECT id FROM attendance_adjustment_requests
                WHERE teacher_id=? AND work_date=? AND request_type=?
                  AND status IN ('pending','approved')
                  AND (? != 'schedule_change' OR status='pending')
                """,
                (teacher["id"], work_date, request_type, request_type),
            ).fetchone()
            if duplicate:
                message = "선택한 날짜에 처리 대기 중인 요청이 있습니다." if request_type == "schedule_change" else "오늘 같은 종류의 요청이 이미 등록되어 있습니다."
                self.send_json({"error": message}, HTTPStatus.CONFLICT)
                return
            effective_plan = connection.execute(
                """
                SELECT start_time,end_time FROM attendance_adjustment_requests
                WHERE teacher_id=? AND work_date=? AND request_type='schedule_change' AND status='approved'
                ORDER BY reviewed_at DESC LIMIT 1
                """,
                (teacher["id"], work_date),
            ).fetchone()
            plan_start = time_minutes(effective_plan["start_time"] if effective_plan else plan["start_time"])
            plan_end = time_minutes(effective_plan["end_time"] if effective_plan else plan["end_time"])
            if request_type == "schedule_change":
                start_time = str(payload.get("startTime", ""))[:5]
                end_time = str(payload.get("endTime", ""))[:5]
                requested_start = time_minutes(start_time)
                requested_end = time_minutes(end_time)
                if requested_end <= requested_start:
                    self.send_json({"error": "변경 퇴근 시간은 출근 시간보다 늦어야 합니다."}, HTTPStatus.BAD_REQUEST)
                    return
            elif request_type == "early_leave":
                start_time = ""
                end_time = str(payload.get("endTime", ""))[:5]
                requested_end = time_minutes(end_time)
                if requested_end <= plan_start or requested_end >= plan_end:
                    self.send_json({"error": "조퇴 시간은 예정 출근 이후, 예정 퇴근 이전이어야 합니다."}, HTTPStatus.BAD_REQUEST)
                    return
            else:
                start_time = str(payload.get("startTime", ""))[:5]
                end_time = str(payload.get("endTime", ""))[:5]
                requested_start = time_minutes(start_time)
                requested_end = time_minutes(end_time)
                if requested_end <= requested_start:
                    self.send_json({"error": "추가근무 종료 시간은 시작 시간보다 늦어야 합니다."}, HTTPStatus.BAD_REQUEST)
                    return
                if not (requested_end <= plan_start or requested_start >= plan_end):
                    self.send_json({"error": "추가근무 시간은 정규 근무시간과 겹치지 않게 입력해 주세요."}, HTTPStatus.BAD_REQUEST)
                    return
            cursor = connection.execute(
                """
                INSERT INTO attendance_adjustment_requests(
                  teacher_id,request_type,work_date,start_time,end_time,reason,requested_at
                ) VALUES (?,?,?,?,?,?,?)
                """,
                (teacher["id"], request_type, work_date, start_time, end_time, reason, iso_now()),
            )
        self.send_json({"ok": True, "requestId": cursor.lastrowid}, HTTPStatus.CREATED)

    def create_attendance_request(self):
        teacher = self.current_teacher()
        if not teacher:
            self.send_json({"error": "로그인이 필요합니다."}, HTTPStatus.UNAUTHORIZED)
            return
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        event_type = payload.get("eventType")
        if event_type not in {"clock_in", "clock_out"}:
            self.send_json({"error": "출근 또는 퇴근 요청만 가능합니다."}, HTTPStatus.BAD_REQUEST)
            return
        today = now_kst().date().isoformat()
        day = day_key_for_date(today)
        with db() as connection:
            plan = connection.execute(
                "SELECT id FROM teacher_work_schedule WHERE academy_teacher_id=? AND day=?",
                (teacher["academy_teacher_id"] or "", day),
            ).fetchone()
            if not plan:
                self.send_json({"error": "오늘의 근무시간이 등록되지 않았습니다. 원장님께 먼저 등록을 요청해 주세요."}, HTTPStatus.CONFLICT)
                return
            duplicate = connection.execute(
                "SELECT id FROM attendance_requests WHERE teacher_id=? AND work_date=? AND event_type=? AND status IN ('pending','approved')",
                (teacher["id"], today, event_type),
            ).fetchone()
            if duplicate:
                self.send_json({"error": "오늘 같은 요청이 이미 등록되어 있습니다."}, HTTPStatus.CONFLICT)
                return
            if event_type == "clock_out":
                clock_in = connection.execute(
                    "SELECT id FROM attendance_requests WHERE teacher_id=? AND work_date=? AND event_type='clock_in' AND status='approved'",
                    (teacher["id"], today),
                ).fetchone()
                if not clock_in:
                    self.send_json({"error": "원장님이 출근 요청을 승인한 뒤 퇴근을 요청할 수 있습니다."}, HTTPStatus.CONFLICT)
                    return
            cursor = connection.execute(
                "INSERT INTO attendance_requests(teacher_id,event_type,work_date,requested_at) VALUES (?,?,?,?)",
                (teacher["id"], event_type, today, iso_now()),
            )
        self.send_json({"ok": True, "requestId": cursor.lastrowid}, HTTPStatus.CREATED)

    def review_attendance(self, path):
        if not self.owner_allowed():
            self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 사용할 수 있습니다."}, HTTPStatus.FORBIDDEN)
            return
        parts = path.strip("/").split("/")
        if len(parts) != 5 or not parts[3].isdigit() or parts[4] not in {"approve", "reject"}:
            self.send_json({"error": "잘못된 승인 요청입니다."}, HTTPStatus.BAD_REQUEST)
            return
        request_id = int(parts[3])
        status = "approved" if parts[4] == "approve" else "rejected"
        with db() as connection:
            row = connection.execute("SELECT * FROM attendance_requests WHERE id=?", (request_id,)).fetchone()
            if not row:
                self.send_json({"error": "요청을 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
                return
            if row["status"] != "pending":
                self.send_json({"error": "이미 처리된 요청입니다."}, HTTPStatus.CONFLICT)
                return
            if status == "approved" and row["event_type"] == "clock_out":
                clock_in = connection.execute(
                    "SELECT id FROM attendance_requests WHERE teacher_id=? AND work_date=? AND event_type='clock_in' AND status='approved'",
                    (row["teacher_id"], row["work_date"]),
                ).fetchone()
                if not clock_in:
                    self.send_json({"error": "출근 승인 기록이 없어 퇴근을 승인할 수 없습니다."}, HTTPStatus.CONFLICT)
                    return
            connection.execute(
                "UPDATE attendance_requests SET status=?, reviewed_at=? WHERE id=?",
                (status, iso_now(), request_id),
            )
        self.send_json({"ok": True, "status": status})

    def review_attendance_adjustment(self, path):
        if not self.owner_allowed():
            self.send_json({"error": "원장 화면은 학원 컴퓨터에서만 사용할 수 있습니다."}, HTTPStatus.FORBIDDEN)
            return
        parts = path.strip("/").split("/")
        if len(parts) != 5 or not parts[3].isdigit() or parts[4] not in {"approve", "reject"}:
            self.send_json({"error": "잘못된 승인 요청입니다."}, HTTPStatus.BAD_REQUEST)
            return
        request_id = int(parts[3])
        status = "approved" if parts[4] == "approve" else "rejected"
        with db() as connection:
            row = connection.execute(
                "SELECT * FROM attendance_adjustment_requests WHERE id=?", (request_id,)
            ).fetchone()
            if not row:
                self.send_json({"error": "요청을 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
                return
            if row["status"] != "pending":
                self.send_json({"error": "이미 처리된 요청입니다."}, HTTPStatus.CONFLICT)
                return
            connection.execute(
                "UPDATE attendance_adjustment_requests SET status=?, reviewed_at=? WHERE id=?",
                (status, iso_now(), request_id),
            )
        self.send_json({"ok": True, "status": status})


def configure_owner_password() -> None:
    print("이지매쓰 원장 계정 비밀번호 설정")
    password = getpass("새 비밀번호(4자 이상): ")
    confirmation = getpass("비밀번호 확인: ")
    if password != confirmation:
        raise SystemExit("비밀번호가 서로 다릅니다.")
    try:
        set_owner_password(password)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print("원장 계정(owner) 비밀번호를 안전하게 저장했습니다.")


def main() -> None:
    init_db()
    if len(sys.argv) > 1:
        if sys.argv[1:] == ["set-owner-password"]:
            configure_owner_password()
            return
        raise SystemExit("사용법: python server.py [set-owner-password]")
    host = os.environ.get("ACADEMY_HOST", "127.0.0.1")
    port = int(os.environ.get("ACADEMY_PORT", "49321"))
    print(f"이지매쓰 서버: http://{host}:{port}/")
    print(f"선생님 앱: http://{host}:{port}/teacher.html")
    if not os.environ.get("KAKAO_REST_API_KEY"):
        print("카카오 로그인: 설정 전 (KAKAO_REST_API_KEY 필요)")
    if not owner_is_configured():
        print("원장 로그인: 설정 전 (python server.py set-owner-password 실행 필요)")
    ThreadingHTTPServer((host, port), AcademyHandler).serve_forever()


if __name__ == "__main__":
    main()
