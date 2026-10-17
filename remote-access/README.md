# 이지매쓰 원격 설치 준비

원장님 Windows 노트북에 Tailscale과 Windows OpenSSH를 이용한 비공개 유지보수 통로를 준비한다.

## 보안 구조

- 인터넷 공유기의 포트를 열지 않는다.
- Windows SSH 방화벽은 패키지를 만든 Mac의 현재 Tailscale IPv4·IPv6 주소만 허용한다.
- 비밀번호 대신 Mac 전용 Ed25519 공개키를 사용한다.
- 개인키는 `/Users/joseph/.ssh/easymath_owner_remote_ed25519`에만 두며 패키지, Git, 문서에 복사하지 않는다.
- Windows 패키지에는 공개키와 해당 Mac의 Tailscale 주소만 포함한다.
- `REMOVE-REMOTE-ACCESS.cmd`로 공개키와 전용 방화벽 규칙을 제거할 수 있다.

## 패키지 만들기

프로젝트 루트에서 실행한다.

```bash
python3 build_remote_setup.py
```

결과물은 `release/EasyMath-Remote-Setup-YYYY-MM-DD.zip`과 SHA-256 파일이다. Mac의 Tailscale 주소가 바뀌면 패키지를 다시 만든다.

## Windows에서 준비

1. Tailscale을 설치하고 Mac과 같은 tailnet에 로그인한다.
2. ZIP을 풀고 `START-REMOTE-SETUP.cmd`를 실행한다.
3. 바탕화면의 `이지매쓰-원격준비결과.txt`에서 Tailscale 이름/IP와 Windows 사용자를 확인한다.

## Mac에서 확인·접속

```bash
remote-access/mac/check-owner-laptop.sh <Tailscale-IP-또는-DNS> <Windows사용자>
remote-access/mac/connect-owner-laptop.sh <Tailscale-IP-또는-DNS> <Windows사용자>
```

Windows에서 실제 실행하기 전에는 OpenSSH 설치, UAC, 방화벽, 재부팅 후 재접속을 검증한 것으로 간주하지 않는다.
