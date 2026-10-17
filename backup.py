#!/usr/bin/env python3
"""이지매쓰 SQLite와 수업 사진을 일관된 백업 묶음으로 생성·검증한다."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import shutil
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DB_PATH = Path(os.environ.get("ACADEMY_DB_PATH", str(DATA / "academy.sqlite3")))
PHOTO_PATH = Path(os.environ.get("ACADEMY_PHOTO_PATH", str(DATA / "photos")))
BACKUP_PATH = Path(os.environ.get("ACADEMY_BACKUP_PATH", str(DATA / "backups")))
RETENTION_COUNT = max(7, int(os.environ.get("ACADEMY_BACKUP_RETENTION", "30")))
KST = ZoneInfo("Asia/Seoul")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sqlite(path: Path) -> None:
    uri = f"file:{path.resolve().as_posix()}?mode=ro&immutable=1"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()
    if not result or result[0] != "ok":
        raise RuntimeError(f"데이터베이스 무결성 검사 실패: {result}")


def photo_summary(path: Path) -> tuple[int, int]:
    files = [item for item in path.rglob("*") if item.is_file()] if path.is_dir() else []
    return len(files), sum(item.stat().st_size for item in files)


def create_backup() -> Path:
    if not DB_PATH.is_file():
        raise RuntimeError(f"데이터베이스를 찾을 수 없습니다: {DB_PATH}")
    BACKUP_PATH.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(KST).strftime("%Y%m%d-%H%M%S")
    destination = BACKUP_PATH / f"backup-{stamp}"
    if destination.exists():
        raise RuntimeError(f"같은 시각의 백업이 이미 있습니다: {destination}")
    temporary = Path(tempfile.mkdtemp(prefix=".incomplete-", dir=BACKUP_PATH))
    try:
        database_copy = temporary / "academy.sqlite3"
        with closing(sqlite3.connect(DB_PATH)) as source, closing(sqlite3.connect(database_copy)) as target:
            source.backup(target)
        verify_sqlite(database_copy)
        photo_destination = temporary / "photos"
        if PHOTO_PATH.is_dir():
            shutil.copytree(PHOTO_PATH, photo_destination)
        else:
            photo_destination.mkdir()
        photo_count, photo_bytes = photo_summary(photo_destination)
        manifest = {
            "format": 1,
            "createdAt": datetime.now(KST).isoformat(timespec="seconds"),
            "database": {
                "filename": database_copy.name,
                "bytes": database_copy.stat().st_size,
                "sha256": sha256(database_copy),
            },
            "photos": {"directory": "photos", "count": photo_count, "bytes": photo_bytes},
        }
        (temporary / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temporary.rename(destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    prune_old_backups()
    return destination


def prune_old_backups() -> None:
    backups = sorted(
        (path for path in BACKUP_PATH.glob("backup-*") if path.is_dir()),
        key=lambda path: path.name,
        reverse=True,
    )
    for old_backup in backups[RETENTION_COUNT:]:
        shutil.rmtree(old_backup)


def verify_backup(path: Path) -> dict:
    path = path.resolve()
    manifest_path = path / "manifest.json"
    database_path = path / "academy.sqlite3"
    if not manifest_path.is_file() or not database_path.is_file():
        raise RuntimeError("백업에 manifest.json 또는 academy.sqlite3가 없습니다.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_hash = manifest.get("database", {}).get("sha256")
    actual_hash = sha256(database_path)
    if not expected_hash or not hmac_safe_equal(expected_hash, actual_hash):
        raise RuntimeError("백업 데이터베이스 해시가 일치하지 않습니다.")
    verify_sqlite(database_path)
    photo_count, photo_bytes = photo_summary(path / "photos")
    if photo_count != manifest.get("photos", {}).get("count") or photo_bytes != manifest.get("photos", {}).get("bytes"):
        raise RuntimeError("백업 사진 개수 또는 용량이 manifest와 일치하지 않습니다.")
    return manifest


def hmac_safe_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)


def main() -> None:
    parser = argparse.ArgumentParser(description="이지매쓰 운영 데이터 백업")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("create", help="새 백업 생성")
    verify_parser = subparsers.add_parser("verify", help="기존 백업 검증")
    verify_parser.add_argument("path", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        path = create_backup()
        print(f"백업 완료: {path}")
    else:
        manifest = verify_backup(args.path)
        print(f"백업 정상: {args.path} ({manifest['createdAt']})")


if __name__ == "__main__":
    main()
