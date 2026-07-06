#!/usr/bin/env python3
"""Upload MP3 to QQ Bot (base64) → send as native voice message."""
import base64, json, os, sys, time
from urllib.request import Request, urlopen

QQ_APP_ID = os.environ.get("QQ_APP_ID", "")
QQ_CLIENT_SECRET = os.environ.get("QQ_CLIENT_SECRET", "")
QQ_HOME = os.environ.get("QQBOT_HOME_CHANNEL", "")
AUDIO = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bailian_tts_qq.mp3"
API = "https://api.sgroup.qq.com"

def post(url, headers=None, body=None):
    headers = headers or {}
    data = json.dumps(body).encode() if isinstance(body, dict) else body
    headers.setdefault("Content-Type", "application/json")
    rq = Request(url, data=data, headers=headers, method="POST")
    try:
        with urlopen(rq, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        if hasattr(e, 'read'):
            err = e.read().decode(errors='replace')
            print(f"    HTTP {e.code}: {err[:500]}", file=sys.stderr)
        raise

# Token
r = post("https://bots.qq.com/app/getAppAccessToken",
         body={"appId": QQ_APP_ID, "clientSecret": QQ_CLIENT_SECRET})
token = r["access_token"]
h = {"Authorization": f"QQBot {token}"}
print(f"Token OK")

# Upload
size = os.path.getsize(AUDIO)
with open(AUDIO, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
r = post(f"{API}/v2/users/{QQ_HOME}/files", h, {
    "file_type": 3,  # VOICE
    "file_data": b64,
    "srv_send_msg": False,
})
fid = r.get("file_info")
print(f"Upload OK: file_info={fid[:40] if fid else 'MISSING'}...")
if not fid:
    sys.exit(1)

# Send
r = post(f"{API}/v2/users/{QQ_HOME}/messages", h, {
    "msg_type": 7,  # MEDIA
    "media": {"file_info": fid},
})
print(f"Send: {json.dumps(r, ensure_ascii=False)[:300]}")
print("✓ DONE" if r.get("id") else "³ check QQ")
