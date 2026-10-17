# 이지매쓰 메시지 연결기 규격

학원 프로그램과 개인 카카오톡은 직접 묶지 않는다. 학원 서버는 아래 HTTP 규격만 사용하고, 실제 설치 장소가 확정되면 카카오톡이 로그인된 장치에 맞는 드라이버를 연결한다.

## 학원 서버가 기대하는 규격

- `GET /status` → `{ "ready": true }`
- `GET /rooms` → `{ "rooms": [{ "chat_id": "...", "title": "..." }] }`
- `GET /messages?chat_id=...&limit=20` → `{ "messages": [...] }`
- `POST /send` + `{ "chat_id": "...", "message": "..." }` → `{ "status": "sent" | "unknown" }`
- 모든 요청은 `Authorization: Bearer <token>`을 사용한다.

`kakao_bridge.py`는 이 규격의 참조 구현이다. `KAKAO_DRIVER_CLI`에 실제 장치용 송수신기 실행 파일을 지정해야 하며, 프로그램이 현재 컴퓨터나 개인 계정을 자동 선택하지 않는다.

## 배포 시 선택

- 학원 프로그램과 카카오톡이 같은 장치: `ACADEMY_MESSAGING_CONNECTOR_CLI`에 호환 CLI 경로를 지정한다.
- 클라우드 서버와 카카오톡 장치가 분리됨: 카카오 장치에서 이 브리지를 실행하고, 학원 서버에 `ACADEMY_MESSAGING_CONNECTOR_URL`과 같은 토큰을 설정한다.
- 아직 설치 장치가 정해지지 않음: 아무 값도 설정하지 않는다. 카톡 연결 관리 화면은 준비 상태로 남고 수동 복사는 계속 사용할 수 있다.

카카오 비밀번호, 세션, 토큰은 Git에 저장하지 않는다. 브리지의 외부 접속은 HTTPS 또는 Tailscale 같은 사설망 안에서만 허용한다. 전송 결과가 `unknown`이면 자동 재전송하지 않고 카카오톡에서 직접 확인한다.
