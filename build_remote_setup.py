#!/usr/bin/env python3
"""Mac 공개키와 Tailscale 주소를 포함한 Windows 원격 설치 준비 ZIP을 만든다."""

from __future__ import annotations

import hashlib
import ipaddress
import shutil
import stat
import subprocess
import zipfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RELEASE = ROOT / "release"
SOURCE = ROOT / "remote-access" / "windows"
PUBLIC_KEY = Path("/Users/joseph/.ssh/easymath_owner_remote_ed25519.pub")
PRIVATE_KEY = Path("/Users/joseph/.ssh/easymath_owner_remote_ed25519")
PACKAGE_NAME = f"EasyMath-Remote-Setup-OFFLINE-{date.today().isoformat()}"
OFFLINE_INSTALLERS = {
    "OpenSSH-Win64-v10.0.0.0.msi": "ddec9c53864280759cf9f74791cefd387100e3946aa849a1c138a4ed1b96b7d9",
    "OpenSSH-ARM64-v10.0.0.0.msi": "7a17d0e22d004fb47ca4bfd8fef926fa305de4ebf70a6f3c7a29c39aabef0023",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def validate_key_files() -> None:
    if not PUBLIC_KEY.is_file() or not PRIVATE_KEY.is_file():
        raise SystemExit("이지매쓰 원격 유지보수용 SSH 키가 없습니다.")
    public_text = PUBLIC_KEY.read_text(encoding="utf-8").strip()
    if not public_text.startswith("ssh-ed25519 "):
        raise SystemExit("공개키 형식이 올바르지 않습니다.")
    private_mode = stat.S_IMODE(PRIVATE_KEY.stat().st_mode)
    if private_mode & 0o077:
        raise SystemExit(f"개인키 권한이 너무 넓습니다: {oct(private_mode)}")


def tailscale_addresses() -> list[str]:
    executable = Path("/usr/local/bin/tailscale")
    if not executable.is_file():
        raise SystemExit("Mac의 Tailscale 명령을 찾을 수 없습니다.")
    addresses: list[str] = []
    for family in ("-4", "-6"):
        result = subprocess.run(
            [str(executable), "ip", family],
            check=True,
            capture_output=True,
            text=True,
        )
        for value in result.stdout.splitlines():
            value = value.strip()
            if value:
                ipaddress.ip_address(value)
                addresses.append(value)
    if not addresses:
        raise SystemExit("Mac의 Tailscale 주소를 확인할 수 없습니다.")
    return addresses


def build() -> Path:
    validate_key_files()
    for filename, expected_hash in OFFLINE_INSTALLERS.items():
        installer = SOURCE / "offline" / filename
        if not installer.is_file():
            raise SystemExit(f"오프라인 OpenSSH 설치파일이 없습니다: {filename}")
        actual_hash = sha256(installer)
        if actual_hash != expected_hash:
            raise SystemExit(
                f"오프라인 OpenSSH 설치파일 해시가 올바르지 않습니다: {filename}"
            )
    RELEASE.mkdir(exist_ok=True)
    stage = RELEASE / PACKAGE_NAME
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(SOURCE, stage)

    # Windows PowerShell 5.1은 BOM 없는 UTF-8을 ANSI로 해석한다.
    # cmd.exe는 LF 전용 배치 파일을 줄 단위로 안정적으로 실행하지 못하므로
    # 배치 파일은 BOM 없는 UTF-8 + CRLF로 고정한다.
    for script in stage.glob("*.cmd"):
        text = script.read_text(encoding="utf-8-sig")
        with script.open("w", encoding="utf-8", newline="\r\n") as output:
            output.write(text)

    for script in stage.glob("*.ps1"):
        text = script.read_text(encoding="utf-8-sig")
        with script.open("w", encoding="utf-8-sig", newline="\r\n") as output:
            output.write(text)

    assets = stage / "assets"
    assets.mkdir()
    shutil.copy2(PUBLIC_KEY, assets / "mac-maintenance-key.pub")
    (assets / "mac-tailscale-addresses.txt").write_text(
        "\n".join(tailscale_addresses()) + "\n",
        encoding="ascii",
    )

    archive = RELEASE / f"{PACKAGE_NAME}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                bundle.write(path, Path(PACKAGE_NAME) / path.relative_to(stage))
    shutil.rmtree(stage)

    with zipfile.ZipFile(archive) as bundle:
        member_names = bundle.namelist()
        if any(name.endswith("easymath_owner_remote_ed25519") for name in member_names):
            raise SystemExit("개인키가 패키지에 포함되었습니다. 결과물을 사용하지 마세요.")
        if not any(name.endswith("assets/mac-maintenance-key.pub") for name in member_names):
            raise SystemExit("공개키가 패키지에 없습니다.")
        if not any(name.endswith("assets/mac-tailscale-addresses.txt") for name in member_names):
            raise SystemExit("Mac Tailscale 주소가 패키지에 없습니다.")
        for filename, expected_hash in OFFLINE_INSTALLERS.items():
            members = [name for name in member_names if name.endswith(f"offline/{filename}")]
            if len(members) != 1:
                raise SystemExit(f"오프라인 OpenSSH 설치파일 구성이 올바르지 않습니다: {filename}")
            if hashlib.sha256(bundle.read(members[0])).hexdigest() != expected_hash:
                raise SystemExit(f"ZIP 안의 OpenSSH 설치파일 해시가 올바르지 않습니다: {filename}")
        for name in member_names:
            content = bundle.read(name)
            if b"BEGIN OPENSSH PRIVATE KEY" in content:
                raise SystemExit("개인키 내용이 패키지에 포함되었습니다. 결과물을 사용하지 마세요.")
            if name.lower().endswith(".cmd"):
                if content.startswith(b"\xef\xbb\xbf"):
                    raise SystemExit(f"배치 파일에 UTF-8 BOM이 있습니다: {name}")
                if b"\n" in content and content.count(b"\r\n") != content.count(b"\n"):
                    raise SystemExit(f"배치 파일 줄바꿈이 CRLF가 아닙니다: {name}")

    checksum = RELEASE / f"{PACKAGE_NAME}.sha256"
    checksum.write_text(f"{sha256(archive)}  {archive.name}\n", encoding="utf-8")
    return archive


if __name__ == "__main__":
    print(build())
