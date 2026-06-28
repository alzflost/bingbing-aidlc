#!/usr/bin/env bash
# Atlassian OAuth 2.0 공용 인증 관리 스크립트
# 여러 Confluence 스킬(md2cf, html2cf, cf2md 등)이 공유하는 단일 인증 스크립트
#
# 상태를 자동 감지하여 필요한 처리만 수행:
#   Case 0. confluence-secret.json 없음  → .env.local 안내 + 3LO 로그인
#   Case 1. refresh_token/cloud_id 없음  → 3LO 재로그인
#   Case 2. access_token 없음             → 리프레시 토큰으로 발급
#   Case 3. access_token 만료             → 리프레시 토큰으로 갱신
#   Case 4. 모두 정상                     → 즉시 exit 0
#
# Exit codes:
#   0: 인증 완료
#   1: 설정 오류 또는 로그인 실패
#
# confluence-secret.json 저장 위치: 이 스크립트와 동일한 디렉토리
#   → 설치 후: ~/.claude/skills/atlassian/confluence-secret.json
#   → 개발 중: skills-share/atlassian/confluence-secret.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECRET_FILE="$SCRIPT_DIR/confluence-secret.json"
REDIRECT_URI="http://localhost:8080/callback"

# .env.local 로드: CWD 우선, SCRIPT_DIR 2단계 상위 폴백
ENV_FILE=""
if [[ -f "$(pwd)/.env.local" ]]; then
  ENV_FILE="$(pwd)/.env.local"
elif [[ -f "${SCRIPT_DIR}/../../.env.local" ]]; then
  ENV_FILE="${SCRIPT_DIR}/../../.env.local"
fi

if [[ -n "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

python3 - "$SECRET_FILE" "$REDIRECT_URI" "${ATLASSIAN_CLIENT_ID:-}" "${ATLASSIAN_CLIENT_SECRET:-}" <<'PYEOF'
import sys, json, webbrowser, urllib.parse, urllib.request, urllib.error
import http.server
from pathlib import Path

SECRET_FILE   = Path(sys.argv[1])
REDIRECT_URI  = sys.argv[2]
ENV_CLIENT_ID     = sys.argv[3] if len(sys.argv) > 3 else ""
ENV_CLIENT_SECRET = sys.argv[4] if len(sys.argv) > 4 else ""
PORT = 8080
SCOPES = " ".join([
    "read:content:confluence",
    "write:content:confluence",
    "read:content-details:confluence",
    "read:page:confluence",
    "write:page:confluence",
    "read:attachment:confluence",
    "write:attachment:confluence",
    "read:content.metadata:confluence",
    "read:hierarchical-content:confluence",
    "read:space:confluence",
    "offline_access",
])

# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def load_secret() -> "dict | None":
    if not SECRET_FILE.exists():
        return None
    try:
        return json.loads(SECRET_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_secret(data: dict) -> None:
    SECRET_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def test_access_token(token: str) -> bool:
    try:
        req = urllib.request.Request(
            "https://api.atlassian.com/oauth/token/accessible-resources",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        return e.code not in (401, 403)
    except Exception:
        return False

def do_refresh(secret: dict) -> "dict | None":
    print("🔄 리프레시 토큰으로 액세스 토큰 갱신 중...")
    req = urllib.request.Request(
        "https://auth.atlassian.com/oauth/token",
        data=json.dumps({
            "grant_type":    "refresh_token",
            "client_id":     secret["client_id"],
            "client_secret": secret["client_secret"],
            "refresh_token": secret["refresh_token"],
        }).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            token_data = json.loads(r.read())
        secret["access_token"]  = token_data["access_token"]
        secret["refresh_token"] = token_data.get("refresh_token", secret["refresh_token"])
        secret["expires_in"]    = token_data.get("expires_in", 3600)
        save_secret(secret)
        print("✅ 액세스 토큰 갱신 완료")
        return secret
    except urllib.error.HTTPError as e:
        print(f"❌ 갱신 실패: {e.read().decode()}")
        return None

def do_login(secret: dict) -> "dict | None":
    client_id     = ENV_CLIENT_ID or secret.get("client_id", "")
    client_secret = ENV_CLIENT_SECRET or secret.get("client_secret", "")

    if not client_id:
        print("\ndeveloper.atlassian.com 에서 생성한 OAuth 앱 정보를 입력하세요.")
        print("(Callback URL: http://localhost:8080/callback 등록 필요)")
        print(".env.local 에 ATLASSIAN_CLIENT_ID, ATLASSIAN_CLIENT_SECRET 설정 권장\n")
        client_id     = input("Client ID     : ").strip()
        client_secret = input("Client Secret : ").strip()

    auth_url = (
        "https://auth.atlassian.com/authorize"
        f"?audience=api.atlassian.com"
        f"&client_id={urllib.parse.quote(client_id)}"
        f"&scope={urllib.parse.quote(SCOPES)}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&prompt=consent"
    )
    print("\n🌐 브라우저에서 Atlassian 로그인을 진행해주세요...")
    if not webbrowser.open(auth_url):
        print(f"   ↳ 아래 URL을 브라우저에서 여세요:\n   {auth_url}")
    print(f"⏳ 콜백 대기 중 (localhost:{PORT})...")

    code_holder = []
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code   = params.get("code",  [""])[0]
            error  = params.get("error", [""])[0]
            code_holder.append(code)
            msg = "✅ 인증 완료! 이 창을 닫아도 됩니다." if code else f"❌ 오류: {error}"
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<h2>{msg}</h2>".encode())
        def log_message(self, *args): pass

    with http.server.HTTPServer(("localhost", PORT), Handler) as httpd:
        httpd.handle_request()

    if not code_holder or not code_holder[0]:
        print("❌ 인증 코드를 받지 못했습니다.")
        return None

    print("✅ 인증 코드 수신")

    try:
        req = urllib.request.Request(
            "https://auth.atlassian.com/oauth/token",
            data=json.dumps({
                "grant_type":    "authorization_code",
                "client_id":     client_id,
                "client_secret": client_secret,
                "code":          code_holder[0],
                "redirect_uri":  REDIRECT_URI,
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as r:
            token_data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"❌ 토큰 교환 실패: {e.read().decode()}")
        return None

    print("✅ 토큰 발급 완료")

    res_req = urllib.request.Request(
        "https://api.atlassian.com/oauth/token/accessible-resources",
        headers={"Authorization": f"Bearer {token_data['access_token']}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(res_req) as r:
        resources = json.loads(r.read())

    if not resources:
        print("❌ 접근 가능한 Atlassian 사이트가 없습니다.")
        return None

    site = resources[0]
    if len(resources) > 1:
        print("\n접근 가능한 Atlassian 사이트:")
        for i, res in enumerate(resources):
            print(f"  [{i}] {res['name']} ({res['url']})")
        idx = int(input("사용할 사이트 번호: ").strip())
        site = resources[idx]

    secret.update({
        "client_id":     client_id,
        "client_secret": client_secret,
        "access_token":  token_data.get("access_token", ""),
        "refresh_token": token_data.get("refresh_token", ""),
        "token_type":    token_data.get("token_type", "Bearer"),
        "expires_in":    token_data.get("expires_in", 3600),
        "cloud_id":      site["id"],
        "cloud_url":     site["url"],
    })
    save_secret(secret)
    print(f"✅ 사이트: {site['name']} ({site['url']})")
    return secret

# ── 메인 ──────────────────────────────────────────────────────────────────────

secret = load_secret()

# Case 0: confluence-secret.json 없음
if secret is None:
    print("=" * 52)
    print("  confluence-secret.json 이 없습니다")
    print("=" * 52)
    print("\n📋 .env.local 에 다음 두 항목을 설정하세요:\n")
    print("   CONFLUENCE_SPACE_KEY=<스페이스 키, 예: T>")
    print("   CONFLUENCE_ACCOUNT_ID=<Atlassian 계정 ID>")
    print("\n이제 Atlassian 로그인을 시작합니다...")
    secret = {}
    secret = do_login(secret)
    if secret is None:
        sys.exit(1)
    print(f"\n✅ {SECRET_FILE} 생성 완료")
    print("⚠️  위의 .env.local 설정을 완료한 뒤 다시 실행하세요.")
    sys.exit(0)

# Case 1: refresh_token 또는 cloud_id 없음 → 재로그인
if not secret.get("refresh_token") or not secret.get("cloud_id"):
    print("🔑 인증 정보가 불완전합니다. 다시 로그인합니다...")
    secret = do_login(secret)
    if secret is None:
        sys.exit(1)
    sys.exit(0)

# Case 2: access_token 없음 → 리프레시로 발급
if not secret.get("access_token"):
    result = do_refresh(secret)
    if result is None:
        print("⚠️  리프레시 실패. 다시 로그인합니다...")
        if do_login(secret) is None:
            sys.exit(1)
    sys.exit(0)

# Case 3: access_token 만료 확인 → 리프레시로 갱신
if not test_access_token(secret["access_token"]):
    print("⏰ 액세스 토큰이 만료되었습니다.")
    result = do_refresh(secret)
    if result is None:
        print("⚠️  리프레시 실패. 다시 로그인합니다...")
        if do_login(secret) is None:
            sys.exit(1)
    sys.exit(0)

# Case 4: 모두 정상
print("✅ 인증 확인 완료")
sys.exit(0)

PYEOF
