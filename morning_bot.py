from notion_client import Client
import requests
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = "911913ff6b1743fa97fec592d0f0881b"
DATA_SOURCE_ID = os.getenv("DATA_SOURCE_ID")
LINE_TOKEN = os.getenv("LINE_TOKEN")
USER_ID = os.getenv("USER_ID")
url_line = "https://api.line.me/v2/bot/message/push"

# スケジュールリスト作成関数
def get_today_schedule():
    
    SERVICE_ACCOUNT_FILE = "service_account.json"
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    CALENDAR_ID = "windtrue12@gmail.com"

    # Google Calendar API認証
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    service = build("calendar", "v3", credentials=credentials)
    
    # 日本時間
    jst = ZoneInfo("Asia/Tokyo")
    today = datetime.now(jst)

    # 今日の0時
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)

    # 明日の0時
    end = start + timedelta(days=1)

    # 今日の予定を取得
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    schedules = []

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        dt = datetime.fromisoformat(start)
        schedules.append(f"{dt.strftime('%H:%M')}　{event['summary']}")
	
	return schedules

    
# タスクリスト作成関数
def get_notion_tasks():

    notion = Client(auth=NOTION_TOKEN)

    response = notion.data_sources.query(
        data_source_id=DATA_SOURCE_ID
    )

    tasks = []

    for row in response["results"]:
        active = row["properties"]["Active"]["checkbox"]
        time = row["properties"]["Time"]["select"]["name"]

        if active and time == "朝":
            routine = row["properties"]["Routine"]["title"][0]["plain_text"]
            tasks.append(f"✅ {routine}")

    return tasks

# メッセージ作成関数
def send_line(message):
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    return requests.post(url_line, headers=headers, json=data)

tasks = get_notion_tasks()
schedules = get_today_schedule()

# メッセージ作成
message = "☀️おはよう！\n\n"

message += "📅 本日の予定\n"

if schedules:
    message += "\n".join(schedules)
else:
    message += "予定はありません！"

message += "\n\n"

message += "今日の朝ルーティン\n"
message += "\n".join(tasks)

send_line(message)
