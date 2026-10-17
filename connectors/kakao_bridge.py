#!/usr/bin/env python3
"""이지매쓰 메시지 연결기.

학원 서버와 카카오톡이 로그인된 장치를 분리할 때 사용하는 작은 HTTP 어댑터다.
실제 UI 제어 드라이버는 KAKAO_DRIVER_CLI로 명시해야 하며 자동 선택하지 않는다.
"""

from __future__ import annotations

import hmac
import json
import os
import subprocess
import threading
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SEND_LOCK = threading.Lock()


def driver_path() -> str:
    value = os.environ.get("KAKAO_DRIVER_CLI", "").strip()
    if not value or not Path(value).is_file():
        raise RuntimeError("KAKAO_DRIVER_CLI를 실제 송수신기 실행 파일로 설정해 주세요.")
    return value


def run_driver(arguments: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        [driver_path(), *arguments], capture_output=True, text=True, timeout=timeout, check=False
    )


def driver_json(arguments: list[str], timeout: int = 30):
    result = run_driver(arguments, timeout)
    if result.returncode != 0:
        raise RuntimeError("카카오 송수신기 실행에 실패했습니다.")
    return json.loads(result.stdout)


def rooms_payload():
    payload = driver_json(["chats", "--json", "--limit", "100"])
    rooms = payload if isinstance(payload, list) else payload.get("rooms", payload.get("chats", []))
    return rooms if isinstance(rooms, list) else []


def messages_payload(chat_id: str, limit: int):
    payload = driver_json(
        ["read", "--chat-id", chat_id, "--limit", str(limit), "--json"], 45
    )
    messages = payload if isinstance(payload, list) else payload.get("messages", [])
    return messages if isinstance(messages, list) else []


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "EasyMathKakaoBridge/1.0"

    def log_message(self, fmt, *args):
        # 메시지 본문과 토큰은 로그에 남기지 않는다.
        print(f"[{self.log_date_time_string()}] {self.command} {self.path.split('?')[0]}")

    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def authorized(self) -> bool:
        token = os.environ.get("KAKAO_BRIDGE_TOKEN", "").strip()
        supplied = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        return bool(token) and hmac.compare_digest(token, supplied)

    def require_auth(self) -> bool:
        if self.authorized():
            return True
        self.send_json({"error": "연결기 인증이 필요합니다."}, HTTPStatus.UNAUTHORIZED)
        return False

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 100_000:
            raise ValueError("요청이 너무 큽니다.")
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        if not self.require_auth():
            return
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/status":
            try:
                result = run_driver(["status"], 10)
                self.send_json({"ready": result.returncode == 0})
            except (OSError, RuntimeError, subprocess.TimeoutExpired):
                self.send_json({"ready": False})
            return
        if parsed.path == "/rooms":
            try:
                self.send_json({"rooms": rooms_payload()})
            except (OSError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError):
                self.send_json({"error": "채팅방을 불러오지 못했습니다."}, HTTPStatus.BAD_GATEWAY)
            return
        if parsed.path == "/messages":
            query = urllib.parse.parse_qs(parsed.query)
            chat_id = query.get("chat_id", [""])[0].strip()[:500]
            try:
                limit = max(1, min(50, int(query.get("limit", ["20"])[0])))
            except ValueError:
                limit = 20
            if not chat_id:
                self.send_json({"error": "chat_id가 필요합니다."}, HTTPStatus.BAD_REQUEST)
                return
            try:
                self.send_json({"messages": messages_payload(chat_id, limit)})
            except (OSError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError):
                self.send_json({"error": "대화를 읽지 못했습니다."}, HTTPStatus.BAD_GATEWAY)
            return
        self.send_json({"error": "지원하지 않는 요청입니다."}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        if not self.require_auth():
            return
        if urllib.parse.urlparse(self.path).path != "/send":
            self.send_json({"error": "지원하지 않는 요청입니다."}, HTTPStatus.NOT_FOUND)
            return
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        chat_id = str(payload.get("chat_id", "")).strip()[:500]
        message = str(payload.get("message", "")).strip()[:6000]
        if not chat_id or len(message) < 1:
            self.send_json({"error": "정확한 채팅방과 메시지가 필요합니다."}, HTTPStatus.BAD_REQUEST)
            return
        if not SEND_LOCK.acquire(blocking=False):
            self.send_json({"error": "다른 메시지를 처리 중입니다."}, HTTPStatus.CONFLICT)
            return
        try:
            try:
                result = run_driver(["send", "--chat-id", chat_id, "--", message], 45)
                sent = result.returncode == 0 and "message sent" in result.stdout.lower()
            except (OSError, RuntimeError, subprocess.TimeoutExpired):
                sent = False
            # 결과 불명은 절대 자동 재전송하지 않는다.
            self.send_json({"status": "sent" if sent else "unknown"})
        finally:
            SEND_LOCK.release()


def main() -> None:
    if not os.environ.get("KAKAO_BRIDGE_TOKEN", "").strip():
        raise SystemExit("KAKAO_BRIDGE_TOKEN을 먼저 설정해 주세요.")
    driver_path()
    host = os.environ.get("KAKAO_BRIDGE_HOST", "127.0.0.1")
    port = int(os.environ.get("KAKAO_BRIDGE_PORT", "49322"))
    print(f"이지매쓰 카카오 연결기: http://{host}:{port}")
    ThreadingHTTPServer((host, port), BridgeHandler).serve_forever()


if __name__ == "__main__":
    main()
