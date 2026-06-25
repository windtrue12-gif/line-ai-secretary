from notion_client import Client
import requests
import os

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = "911913ff6b1743fa97fec592d0f0881b"
DATA_SOURCE_ID = os.getenv("DATA_SOURCE_ID")
LINE_TOKEN = os.getenv("LINE_TOKEN")
USER_ID = os.getenv("USER_ID")
url_line = "https://api.line.me/v2/bot/message/push"


def get_notion_tasks():

    notion = Client(auth=NOTION_TOKEN)

    response = notion.data_sources.query(
        data_source_id=DATA_SOURCE_ID
    )

    tasks = []

    for row in response["results"]:

        active = row["properties"]["Active"]["checkbox"]

        if active:

            routine = row["properties"]["Routine"]["title"][0]["plain_text"]

            tasks.append(f"✅ {routine}")

    return tasks

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

message = "☀️おはよう！\n\n今日の朝ルーティン\n\n"
message += "\n".join(tasks)

send_line(message)
