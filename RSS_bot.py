import requests
from openai import OpenAI
import feedparser

LINE_TOKEN = os.getenv("LINE_TOKEN")
USER_ID = os.getenv("USER_ID")
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

url_line = "https://api.line.me/v2/bot/message/push"
url_feed = "https://hnrss.org/frontpage"

headers = {
    "Authorization": f"Bearer {LINE_TOKEN}",
    "Content-Type": "application/json"
}

feed = feedparser.parse(url_feed)
for entry in feed.entries[:5]:
    print(entry.title)

news = "\n".join(
    [entry.title for entry in feed.entries[:5]]
)

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "user",
            "content": f"""
                以下のニュースを3行で要約して

                {news}
            """
        }
    ]
)

text = response.choices[0].message.content

data = {
    "to": USER_ID,
    "messages": [
        {
            "type": "text",
            "text": text
        }
    ]
}

response = requests.post(url_line, headers=headers, json=data)