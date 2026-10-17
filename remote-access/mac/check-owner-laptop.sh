#!/bin/zsh
set -euo pipefail

readonly key_path="/Users/joseph/.ssh/easymath_owner_remote_ed25519"

if (( $# != 2 )); then
  echo "사용법: $0 <Tailscale-IP-또는-DNS이름> <Windows사용자>" >&2
  exit 64
fi

readonly remote_host="$1"
readonly remote_user="$2"

echo "[1/2] Tailscale 연결 확인"
/usr/local/bin/tailscale ping --timeout=10s "$remote_host"

echo "[2/2] SSH 연결 확인"
/usr/bin/ssh \
  -i "$key_path" \
  -o IdentitiesOnly=yes \
  -o StrictHostKeyChecking=accept-new \
  -o ConnectTimeout=15 \
  -l "$remote_user" \
  "$remote_host" \
  "hostname && whoami"
