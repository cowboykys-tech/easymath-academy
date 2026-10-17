#!/usr/bin/env python3
"""비밀값과 운영 데이터를 제외한 Windows 전달용 ZIP을 만든다."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RELEASE = ROOT / "release"
PACKAGE_NAME = f"EasyMathAcademy-Windows-{date.today().isoformat()}"
INCLUDE_FILES = [
    "AGENTS.md",
    "README.md",
    "PROJECT_CONTEXT.md",
    "HANDOFF_AND_MAINTENANCE.md",
    "WINDOWS_INSTALL.txt",
    "INSTALL-EASYMATH.cmd",
    "server.py",
    "backup.py",
    "requirements.txt",
    ".env.example",
]
INCLUDE_DIRECTORIES = ["dist", "deploy", "connectors"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build() -> Path:
    RELEASE.mkdir(exist_ok=True)
    stage = RELEASE / PACKAGE_NAME
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir()
    for filename in INCLUDE_FILES:
        shutil.copy2(ROOT / filename, stage / filename)
    for dirname in INCLUDE_DIRECTORIES:
        shutil.copytree(ROOT / dirname, stage / dirname)
    # cmd.exe는 LF 전용 배치 파일을 줄 단위로 안정적으로 실행하지 못하므로
    # 배치 파일은 BOM 없는 UTF-8 + CRLF로 고정한다.
    for script in stage.rglob("*.cmd"):
        text = script.read_text(encoding="utf-8-sig")
        with script.open("w", encoding="utf-8", newline="\r\n") as output:
            output.write(text)
    # Windows PowerShell 5.1은 BOM 없는 UTF-8을 ANSI로 해석하므로
    # 한글 경로와 안내 문구가 깨지지 않게 전달본의 PS1만 UTF-8 BOM으로 저장한다.
    for script in stage.rglob("*.ps1"):
        script.write_text(script.read_text(encoding="utf-8"), encoding="utf-8-sig")
    archive = RELEASE / f"{PACKAGE_NAME}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                bundle.write(path, Path(PACKAGE_NAME) / path.relative_to(stage))
    shutil.rmtree(stage)
    with zipfile.ZipFile(archive) as bundle:
        for name in bundle.namelist():
            content = bundle.read(name)
            if b"BEGIN OPENSSH PRIVATE KEY" in content:
                raise SystemExit("개인키가 Windows 전달본에 포함되었습니다. 결과물을 사용하지 마세요.")
            if name.lower().endswith(".cmd"):
                if content.startswith(b"\xef\xbb\xbf"):
                    raise SystemExit(f"배치 파일에 UTF-8 BOM이 있습니다: {name}")
                if b"\n" in content and content.count(b"\r\n") != content.count(b"\n"):
                    raise SystemExit(f"배치 파일 줄바꿈이 CRLF가 아닙니다: {name}")
    checksum = RELEASE / f"{PACKAGE_NAME}.sha256"
    checksum.write_text(f"{sha256(archive)}  {archive.name}\n", encoding="utf-8")
    return archive


if __name__ == "__main__":
    result = build()
    print(result)
