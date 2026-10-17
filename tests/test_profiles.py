import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import server


class ProfileRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = server.DB_PATH
        self.original_photo_path = server.PHOTO_PATH
        server.DB_PATH = Path(self.temp_dir.name) / "academy.sqlite3"
        server.PHOTO_PATH = Path(self.temp_dir.name) / "photos"
        server.PHOTO_PATH.mkdir()
        server.init_db()

    def tearDown(self):
        server.DB_PATH = self.original_db_path
        server.PHOTO_PATH = self.original_photo_path
        self.temp_dir.cleanup()

    def test_profiles_and_schedule_round_trip(self):
        state = {
            "teachers": [{
                "id": "teacher-test", "name": "검증선생", "subject": "사고력 수학",
                "phone": "010-0000-0000", "email": "teacher@example.test", "address": "검증 주소",
                "university": "검증대학교", "major": "수학교육과", "career": "검증 경력",
                "certifications": "검증 자격", "hireDate": "2026-10-17", "employmentType": "시간강사",
                "salaryType": "시급", "salaryAmount": 35000, "notes": "검증 메모", "active": True,
                "classes": ["class-test"],
            }],
            "classes": [{
                "id": "class-test", "name": "검증반", "level": "초등",
                "teacherId": "teacher-test", "students": ["student-test"],
            }],
            "students": [{
                "id": "student-test", "name": "검증학생", "school": "검증초",
                "phone": "010-1111-1111", "grade": "초등 3학년", "classId": "",
                "parent": "검증보호자", "guardianPhone": "010-2222-2222", "address": "검증 주소",
                "birthDate": "2017-01-01", "enrollmentDate": "2026-10-17", "status": "재원",
                "notes": "검증 메모", "latest": "A-1", "focus": "풀이 설명",
            }],
            "records": [], "schedule": [], "weeklyFeedback": [], "attendance": [], "consultations": [],
            "weeklySchedule": [{
                "id": "lesson-test", "day": "mon", "start": "16:00", "end": "17:00",
                "timeLabel": "", "className": "검증반", "subject": "사고력 수학",
                "teacherId": "teacher-test", "studentIds": ["student-test"],
            }],
        }
        with server.db() as connection:
            server.replace_owner_state(connection, state)
            server.replace_teacher_work_schedule(connection, "teacher-test", [{
                "day": "mon", "startTime": "15:30", "endTime": "19:30",
                "breakMinutes": 30, "note": "검증 근무",
            }])
        # 명단 저장은 전체 상태를 다시 쓰므로, 별도 근무계획이 함께 보존되어야 한다.
        with server.db() as connection:
            server.replace_owner_state(connection, state)
        with server.db() as connection:
            restored = server.serialize_owner_state(connection)
            login = connection.execute(
                "SELECT id, active FROM teachers WHERE academy_teacher_id='teacher-test'"
            ).fetchone()
            lesson = connection.execute(
                "SELECT teacher_id, students_json FROM class_schedule WHERE id='lesson-test'"
            ).fetchone()
            work_plan = connection.execute(
                "SELECT * FROM teacher_work_schedule WHERE academy_teacher_id='teacher-test' AND day='mon'"
            ).fetchone()

        self.assertEqual(restored["teachers"][0]["salaryAmount"], 35000)
        self.assertEqual(restored["teachers"][0]["major"], "수학교육과")
        self.assertEqual(restored["students"][0]["guardianPhone"], "010-2222-2222")
        self.assertEqual(restored["weeklySchedule"][0]["studentIds"], ["student-test"])
        self.assertEqual(login["active"], 1)
        self.assertEqual(lesson["teacher_id"], "teacher-test")
        self.assertEqual(json.loads(lesson["students_json"])[0]["name"], "검증학생")
        self.assertEqual(work_plan["start_time"], "15:30")
        self.assertEqual(work_plan["end_time"], "19:30")
        self.assertEqual(work_plan["break_minutes"], 30)

    def test_work_schedule_validation_and_date_helpers(self):
        self.assertEqual(server.time_minutes("09:05"), 545)
        self.assertEqual(server.day_key_for_date("2026-10-17"), "sat")
        self.assertEqual(server.day_key_for_date("2026-10-18"), "sun")
        with self.assertRaises(ValueError):
            server.time_minutes("25:00")
        with server.db() as connection:
            connection.execute(
                "INSERT INTO academy_teachers(id,name,subject,sort_order) VALUES ('teacher-time','시간선생','수학',0)"
            )
            with self.assertRaises(ValueError):
                server.replace_teacher_work_schedule(connection, "teacher-time", [{
                    "day": "mon", "startTime": "18:00", "endTime": "17:00",
                    "breakMinutes": 0, "note": "",
                }])

    def test_existing_work_schedule_migrates_to_support_sunday(self):
        with server.db() as connection:
            connection.execute(
                "INSERT INTO academy_teachers(id,name,subject,sort_order) VALUES ('teacher-sunday','일요선생','수학',0)"
            )
            connection.execute("DROP TABLE teacher_work_schedule")
            connection.execute(
                """
                CREATE TABLE teacher_work_schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    academy_teacher_id TEXT NOT NULL REFERENCES academy_teachers(id) ON DELETE CASCADE,
                    day TEXT NOT NULL CHECK(day IN ('mon','tue','wed','thu','fri','sat')),
                    start_time TEXT NOT NULL, end_time TEXT NOT NULL,
                    break_minutes INTEGER NOT NULL DEFAULT 0,
                    note TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
                    UNIQUE(academy_teacher_id, day)
                )
                """
            )
            connection.execute(
                "INSERT INTO teacher_work_schedule(academy_teacher_id,day,start_time,end_time,break_minutes,note,updated_at) VALUES ('teacher-sunday','sat','10:00','12:00',0,'기존 기록','2026-10-17')"
            )
            server.ensure_sunday_work_schedule(connection)
            preserved = connection.execute(
                "SELECT note FROM teacher_work_schedule WHERE academy_teacher_id='teacher-sunday' AND day='sat'"
            ).fetchone()
            server.replace_teacher_work_schedule(connection, "teacher-sunday", [{
                "day": "sun", "startTime": "13:00", "endTime": "16:00",
                "breakMinutes": 20, "note": "일요일 보충",
            }])
            sunday = connection.execute(
                "SELECT * FROM teacher_work_schedule WHERE academy_teacher_id='teacher-sunday' AND day='sun'"
            ).fetchone()
        self.assertEqual(preserved["note"], "기존 기록")
        self.assertEqual(sunday["end_time"], "16:00")

    def test_existing_adjustments_migrate_to_support_schedule_changes(self):
        with server.db() as connection:
            connection.execute("DROP TABLE attendance_adjustment_requests")
            connection.execute(
                """
                CREATE TABLE attendance_adjustment_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id TEXT NOT NULL REFERENCES teachers(id),
                    request_type TEXT NOT NULL CHECK(request_type IN ('early_leave','overtime')),
                    work_date TEXT NOT NULL, start_time TEXT NOT NULL DEFAULT '',
                    end_time TEXT NOT NULL, reason TEXT NOT NULL, requested_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
                    reviewed_at TEXT, review_note TEXT
                )
                """
            )
            connection.execute(
                "INSERT INTO attendance_adjustment_requests(teacher_id,request_type,work_date,end_time,reason,requested_at) VALUES ('demo1','early_leave','2026-10-17','17:00','기존 조퇴','2026-10-17T10:00:00+09:00')"
            )
            server.ensure_schedule_change_adjustments(connection)
            preserved = connection.execute(
                "SELECT reason FROM attendance_adjustment_requests WHERE request_type='early_leave'"
            ).fetchone()
            connection.execute(
                "INSERT INTO attendance_adjustment_requests(teacher_id,request_type,work_date,start_time,end_time,reason,requested_at) VALUES ('demo1','schedule_change','2026-10-18','11:00','15:00','일요일 보충','2026-10-17T10:05:00+09:00')"
            )
            connection.execute(
                "INSERT INTO attendance_adjustment_requests(teacher_id,request_type,work_date,start_time,end_time,reason,requested_at) VALUES ('demo1','absence','2026-10-19','','','개인 사정','2026-10-17T10:06:00+09:00')"
            )
            changed = connection.execute(
                "SELECT start_time,end_time FROM attendance_adjustment_requests WHERE request_type='schedule_change'"
            ).fetchone()
            absence = connection.execute(
                "SELECT reason FROM attendance_adjustment_requests WHERE request_type='absence'"
            ).fetchone()
        self.assertEqual(preserved["reason"], "기존 조퇴")
        self.assertEqual((changed["start_time"], changed["end_time"]), ("11:00", "15:00"))
        self.assertEqual(absence["reason"], "개인 사정")

    def test_korean_phone_numbers_normalize_for_kakao_linking(self):
        self.assertEqual(server.normalize_phone("010-1234-5678"), "01012345678")
        self.assertEqual(server.normalize_phone("+82 10-1234-5678"), "01012345678")

    def test_kiosk_pairing_is_one_time_and_student_phone_drives_checkin(self):
        state = {
            "teachers": [], "classes": [], "records": [], "schedule": [],
            "weeklyFeedback": [], "attendance": [], "consultations": [], "weeklySchedule": [],
            "students": [{
                "id": "student-checkin", "name": "등원학생", "school": "검증초",
                "phone": "010-1234-5678", "classId": "", "parent": "검증보호자",
                "guardianPhone": "010-9999-0000", "status": "재원", "latest": "", "focus": "",
            }, {
                "id": "student-checkin-2", "name": "동일번호학생", "school": "검증중",
                "phone": "010-8888-5678", "classId": "", "parent": "다른보호자",
                "guardianPhone": "010-7777-0000", "status": "재원", "latest": "", "focus": "",
            }],
        }
        with server.db() as connection:
            server.replace_owner_state(connection, state)
            pairing = server.create_kiosk_pairing_code(connection)
            device = server.pair_kiosk_device(connection, pairing["code"], "입구 태블릿")
            with self.assertRaises(ValueError):
                server.pair_kiosk_device(connection, pairing["code"], "두 번째 태블릿")
            choices = server.record_student_checkin(
                connection, "5678", device["device"]["id"],
                datetime(2026, 10, 17, 15, 20, tzinfo=ZoneInfo("Asia/Seoul")),
            )
            checkin = server.record_student_checkin(
                connection, "5678", device["device"]["id"],
                datetime(2026, 10, 17, 15, 20, tzinfo=ZoneInfo("Asia/Seoul")),
                selected_student_id="student-checkin",
            )
            duplicate = server.record_student_checkin(
                connection, "5678", device["device"]["id"],
                datetime(2026, 10, 17, 15, 30, tzinfo=ZoneInfo("Asia/Seoul")),
                selected_student_id="student-checkin",
            )
            with self.assertRaises(LookupError):
                server.record_student_checkin(connection, "0000", device["device"]["id"])
            stored = connection.execute("SELECT * FROM student_checkins").fetchall()
        self.assertTrue(choices["selectionRequired"])
        self.assertEqual([item["studentName"] for item in choices["candidates"]], ["등원학생", "동일번호학생"])
        self.assertFalse(checkin["duplicate"])
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["student_name"], "등원학생")

    def test_checkin_report_keeps_history_and_builds_weekly_and_monthly_messages(self):
        state = {
            "teachers": [], "classes": [], "records": [], "schedule": [],
            "weeklyFeedback": [], "attendance": [], "consultations": [],
            "students": [{
                "id": "student-report", "name": "리포트학생", "school": "검증초",
                "phone": "010-1111-2222", "classId": "", "parent": "검증보호자",
                "guardianPhone": "010-3333-4444", "status": "재원", "latest": "", "focus": "",
            }],
            "weeklySchedule": [{
                "id": "lesson-report", "day": "sat", "start": "10:00", "end": "11:00",
                "timeLabel": "", "className": "리포트반", "subject": "수학",
                "teacherId": "", "studentIds": ["student-report"],
            }],
        }
        with server.db() as connection:
            server.replace_owner_state(connection, state)
            server.record_student_checkin(
                connection, "2222", "test-device",
                datetime(2026, 10, 17, 10, 5, tzinfo=ZoneInfo("Asia/Seoul")),
            )
            weekly = server.build_checkin_report(connection, "week", "2026-10-17")
            monthly = server.build_checkin_report(connection, "month", "2026-10-17")
            server.replace_owner_state(connection, state)
            preserved = connection.execute("SELECT COUNT(*) AS count FROM student_checkins").fetchone()["count"]
        self.assertEqual((weekly["startDate"], weekly["endDate"]), ("2026-10-12", "2026-10-18"))
        self.assertEqual(weekly["students"][0]["plannedDays"], 1)
        self.assertEqual(weekly["students"][0]["attendanceRate"], 100)
        self.assertIn("주간 등원 리포트", weekly["students"][0]["message"])
        self.assertEqual(monthly["summary"]["totalCheckins"], 1)
        self.assertEqual(preserved, 1)

    def test_student_evaluation_survives_owner_state_replacement(self):
        state = {
            "teachers": [{"id": "teacher-eval", "name": "평가선생", "subject": "수학", "classes": [], "active": True}],
            "classes": [],
            "students": [{"id": "student-eval", "name": "평가학생", "school": "검증초", "classId": "", "parent": "", "latest": "", "focus": ""}],
            "records": [], "schedule": [], "weeklyFeedback": [], "attendance": [], "consultations": [],
            "weeklySchedule": [{
                "id": "lesson-eval", "day": "sat", "start": "10:00", "end": "11:00",
                "timeLabel": "", "className": "평가반", "subject": "분수",
                "teacherId": "teacher-eval", "studentIds": ["student-eval"],
            }],
        }
        with server.db() as connection:
            server.replace_owner_state(connection, state)
            connection.execute(
                """
                INSERT INTO student_evaluations(
                  id,lesson_id,lesson_date,teacher_id,academy_teacher_id,teacher_name,
                  student_id,student_name,class_name,subject,attitude,concentration,
                  understanding,progress,participation,homework,note,created_at,updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    "evaluation-test", "lesson-eval", "2026-10-17", "staff:teacher-eval",
                    "teacher-eval", "평가선생", "student-eval", "평가학생", "평가반", "분수",
                    4, 3, 3, 3, 4, 3, "끝까지 차분히 풀었습니다.", "2026-10-17", "2026-10-17",
                ),
            )
        with server.db() as connection:
            server.replace_owner_state(connection, state)
            saved = connection.execute("SELECT * FROM student_evaluations WHERE id='evaluation-test'").fetchone()
        self.assertIsNotNone(saved)
        self.assertEqual(saved["student_name"], "평가학생")
        self.assertEqual(server.evaluation_as_dict(saved)["scores"]["attitude"]["label"], "매우 좋음")

    def test_student_attendance_and_employment_history_accumulate(self):
        state = {
            "teachers": [{
                "id": "teacher-history", "name": "기록선생", "subject": "수학",
                "hireDate": "2026-01-02", "terminationDate": "", "active": True,
                "classes": [],
            }],
            "classes": [],
            "students": [{
                "id": "student-history", "name": "기록학생", "school": "검증초",
                "classId": "", "parent": "", "enrollmentDate": "2026-03-02",
                "status": "재원", "latest": "A-3", "focus": "풀이 설명",
            }],
            "records": [], "schedule": [], "weeklyFeedback": [], "attendance": [],
            "consultations": [],
            "weeklySchedule": [{
                "id": "lesson-history", "day": "sat", "start": "10:00", "end": "11:00",
                "timeLabel": "", "className": "검증반", "subject": "분수",
                "teacherId": "teacher-history", "studentIds": ["student-history"],
            }],
        }
        with server.db() as connection:
            server.replace_owner_state(connection, state)
            connection.execute(
                """
                INSERT INTO student_attendance_records(
                  lesson_id,lesson_date,teacher_id,academy_teacher_id,teacher_name,
                  student_id,student_name,class_name,subject,attendance_status,note,
                  recorded_at,updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    "lesson-history", "2026-10-17", "staff:teacher-history", "teacher-history",
                    "기록선생", "student-history", "기록학생", "검증반", "분수", "late",
                    "10분 지각", "2026-10-17T10:10:00+09:00", "2026-10-17T10:10:00+09:00",
                ),
            )
        with server.db() as connection:
            server.replace_owner_state(connection, state)
            restored = server.serialize_owner_state(connection)
            attendance = connection.execute(
                "SELECT * FROM student_attendance_records WHERE student_id='student-history'"
            ).fetchone()
            employment = connection.execute(
                "SELECT * FROM teacher_employment_events WHERE academy_teacher_id='teacher-history' AND event_type='hire'"
            ).fetchone()
            student_status = connection.execute(
                "SELECT * FROM student_status_events WHERE student_id='student-history' AND status='재원'"
            ).fetchone()
        self.assertEqual(attendance["attendance_status"], "late")
        self.assertEqual(restored["studentAttendanceSummary"][0]["late"], 1)
        self.assertEqual(employment["effective_date"], "2026-01-02")
        self.assertEqual(student_status["effective_date"], "2026-03-02")

    def test_owner_records_absence_as_approved_without_teacher_request(self):
        today = server.now_kst().date().isoformat()
        day = server.day_key_for_date(today)
        state = {
            "teachers": [{
                "id": "teacher-absence", "name": "결근선생", "subject": "수학",
                "hireDate": "2026-01-02", "active": True, "classes": [],
            }],
            "classes": [], "students": [], "records": [], "schedule": [],
            "weeklyFeedback": [], "attendance": [], "consultations": [],
            "weeklySchedule": [],
        }
        with server.db() as connection:
            server.replace_owner_state(connection, state)
            server.replace_teacher_work_schedule(connection, "teacher-absence", [{
                "day": day, "startTime": "14:00", "endTime": "20:00",
                "breakMinutes": 0, "note": "",
            }])
            record_id = server.record_teacher_absence(
                connection, "teacher-absence", today, "원장 확인 결근"
            )
            saved = connection.execute(
                "SELECT * FROM attendance_adjustment_requests WHERE id=?", (record_id,)
            ).fetchone()
            with self.assertRaisesRegex(ValueError, "이미 있습니다"):
                server.record_teacher_absence(
                    connection, "teacher-absence", today, "중복 결근"
                )
        self.assertEqual(saved["request_type"], "absence")
        self.assertEqual(saved["status"], "approved")
        self.assertEqual(saved["review_note"], "원장 직접 기록")

    def test_feedback_generation_has_safe_fallback_and_parses_structured_output(self):
        original_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            evaluation = {
                "student_name": "평가학생", "class_name": "평가반", "subject": "분수",
                "attitude": 4, "concentration": 3, "understanding": 3,
                "progress": 3, "participation": 4, "homework": 3,
                "note": "분수의 크기를 정확하게 비교하고 풀이 과정을 설명했습니다.",
            }
            message, provider, notice = server.generate_feedback_message(evaluation)
        finally:
            if original_key is not None:
                os.environ["OPENAI_API_KEY"] = original_key
        self.assertEqual(provider, "template")
        self.assertIn("평가학생 학부모님", message)
        self.assertIn("분수의 크기를 정확하게 비교", message)
        self.assertIn("기본 초안", notice)
        response_text = server.extract_response_text({
            "output": [{"content": [{"type": "output_text", "text": '{"message":"검증 문안"}'}]}]
        })
        self.assertEqual(json.loads(response_text)["message"], "검증 문안")

    def test_codex_feedback_uses_ephemeral_read_only_execution(self):
        evaluation = {
            "student_name": "평가학생", "class_name": "평가반", "subject": "분수",
            "attitude": 4, "concentration": 3, "understanding": 3,
            "progress": 3, "participation": 4, "homework": 3,
            "note": "평가학생은 오늘 차분히 참여했습니다.",
        }
        captured = {}

        def fake_run(command, **kwargs):
            captured["command"] = command
            captured["prompt"] = kwargs["input"]
            output_path = Path(command[command.index("-o") + 1])
            output_path.write_text('{"message":"차분하게 개념을 이해했습니다."}', encoding="utf-8")
            return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        with patch.object(server, "codex_binary", return_value="/mock/codex"), patch.object(
            server.subprocess, "run", side_effect=fake_run
        ):
            body = server.codex_feedback_body(evaluation)
        self.assertEqual(body, "차분하게 개념을 이해했습니다.")
        self.assertIn("--ephemeral", captured["command"])
        self.assertIn("read-only", captured["command"])
        self.assertNotIn("평가학생", captured["prompt"])

    def test_connector_room_payload_normalization(self):
        rooms = server.normalized_connector_rooms({
            "chats": [{"chat_id": "room-1", "title": "검증 학부모방"}]
        })
        self.assertEqual(rooms, [{"chatId": "room-1", "title": "검증 학부모방"}])

    def test_parent_room_link_survives_owner_state_refresh(self):
        state = {
            "teachers": [], "classes": [],
            "students": [{
                "id": "student-room", "name": "연결학생", "school": "",
                "classId": "", "parent": "", "latest": "", "focus": "",
            }],
            "records": [], "schedule": [], "weeklyFeedback": [], "attendance": [],
            "consultations": [], "weeklySchedule": [],
        }
        with server.db() as connection:
            server.replace_owner_state(connection, state)
            connection.execute(
                "INSERT INTO kakao_parent_rooms(student_id,chat_id,room_title,linked_at,updated_at) VALUES (?,?,?,?,?)",
                ("student-room", "room-id", "연결 검증방", "2026-10-17", "2026-10-17"),
            )
            server.replace_owner_state(connection, state)
            saved = connection.execute(
                "SELECT room_title FROM kakao_parent_rooms WHERE student_id='student-room'"
            ).fetchone()
        self.assertEqual(saved["room_title"], "연결 검증방")

    def test_message_connector_requires_explicit_deployment_setting(self):
        with patch.dict(os.environ, {}, clear=False):
            old_url = os.environ.pop("ACADEMY_MESSAGING_CONNECTOR_URL", None)
            old_cli = os.environ.pop("ACADEMY_MESSAGING_CONNECTOR_CLI", None)
            try:
                status = server.messaging_connector_status()
            finally:
                if old_url is not None:
                    os.environ["ACADEMY_MESSAGING_CONNECTOR_URL"] = old_url
                if old_cli is not None:
                    os.environ["ACADEMY_MESSAGING_CONNECTOR_CLI"] = old_cli
        self.assertFalse(status["configured"])
        self.assertFalse(status["ready"])


if __name__ == "__main__":
    unittest.main()
