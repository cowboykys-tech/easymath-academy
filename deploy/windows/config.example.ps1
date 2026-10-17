$env:ACADEMY_HOST = "127.0.0.1"
$env:ACADEMY_PORT = "49321"
$env:ACADEMY_DB_PATH = Join-Path $PSScriptRoot "data\academy.sqlite3"
$env:ACADEMY_PHOTO_PATH = Join-Path $PSScriptRoot "data\photos"
$env:ACADEMY_BACKUP_PATH = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "EasyMath Backups"
$env:ACADEMY_BACKUP_RETENTION = "30"
$env:ACADEMY_REQUIRE_OWNER_LOGIN = "1"
# HTTPS 프록시 연결을 완료한 뒤 "1"로 변경합니다.
$env:ACADEMY_HTTPS = "0"
# 운영 도메인이 정해지면 실제 주소로 변경합니다.
$env:KAKAO_REDIRECT_URI = "http://127.0.0.1:49321/auth/kakao/callback"
# AI와 학부모 카톡은 설치 장소가 정해진 뒤 아래 값만 바꿉니다.
$env:ACADEMY_FEEDBACK_AI_PROVIDER = "template"
$env:ACADEMY_CODEX_CLI = ""
$env:ACADEMY_CODEX_FEEDBACK_MODEL = ""
$env:ACADEMY_CODEX_TIMEOUT = "90"
$env:ACADEMY_MESSAGING_CONNECTOR_URL = ""
$env:ACADEMY_MESSAGING_CONNECTOR_CLI = ""
