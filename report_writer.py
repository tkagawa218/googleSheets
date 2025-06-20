import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# === 認証処理 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(credentials)

# === スプレッドシート情報 ===
# 共有されたスプレッドシートのURL or スプレッドシートID
SPREADSHEET_ID = "あなたのスプレッドシートID"  # 例: '1AbCdEfGhIJKLmnOpQrStUvWxYz1234567890'
worksheet = gc.open_by_key(SPREADSHEET_ID).sheet1  # 1番目のシートを開く

# === 日報データ ===
report = {
    "日付": datetime.now().strftime("%Y-%m-%d"),
    "作業内容": "LINE BotのAPI接続テスト",
    "所要時間": "2時間",
    "課題": "Webhookが通らない原因調査",
    "明日の予定": "Google Sheets書き込み処理のLINE連携"
}

# === 行データを1行で追加 ===
row = list(report.values())
worksheet.append_row(row)

print("✅ 日報を書き込みました。")
