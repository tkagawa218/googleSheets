from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import os

app = FastAPI()

# LINE API設定（環境変数 or .env 管理を推奨）
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Google Sheets 認証
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gs = gspread.authorize(credentials)
worksheet = gs.open_by_key("あなたのスプレッドシートID").sheet1

def parse_report(text):
    lines = text.strip().split("\n")
    data = {}
    for line in lines:
        if ":" in line:
            key, val = line.split(":", 1)
            data[key.strip()] = val.strip()
    return data

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_text = body.decode("utf-8")

    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text.startswith("#日報"):
        report = parse_report(text)
        row = [report.get(k, "") for k in ["日付", "作業内容", "所要時間", "課題", "明日の予定"]]
        worksheet.append_row(row)
        reply = "✅ 日報をスプレッドシートに記録しました！"
    else:
        reply = "📋 日報を送るには「#日報」から始めてください。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
