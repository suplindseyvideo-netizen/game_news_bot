import feedparser
import requests
import os
import time

# 1. 구독할 뉴스 사이트의 RSS 주소 목록 (테스트를 위해 모두 '전체 뉴스'로 설정)
RSS_URLS = [
    "https://www.thisisgame.com/rss/",       # 디스이즈게임 (전체)
    "https://www.gamemeca.com/rss/",         # 게임메카 (전체)
    "http://rss.inven.co.kr/rss/news/webzine_total.xml" # ⭐'인기 뉴스'를 '전체 뉴스'로 잠시 변경하여 테스트합니다.⭐
]

# 2. GitHub Secrets에서 슬랙 웹훅 URL 가져오기
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

def send_to_slack(message):
    """슬랙으로 메시지를 전송하는 함수"""
    if not SLACK_WEBHOOK_URL:
        print("에러: SLACK_WEBHOOK_URL이 설정되지 않았습니다. GitHub Secrets를 확인해주세요.")
        return

    payload = {"text": message}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("슬랙 메시지 전송 성공!")
    except requests.exceptions.RequestException as e:
        print(f"에러: 슬랙 메시지 전송 실패 - {e}")

def fetch_news():
    """여러 RSS 피드에서 뉴스를 모아, 최신순 상위 10개를 슬랙으로 전송하는 함수"""
    all_entries = []
    
    for url in RSS_URLS:
        print(f"{url} 에서 뉴스 파싱 시작...")
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
        
    if not all_entries:
        send_to_slack("새로운 뉴스가 없습니다. (테스트 모드)")
        return
        
    all_entries.sort(key=lambda x: x.get("published_parsed", time.gmtime(0)), reverse=True)
    
    latest_entries = all_entries[:10]

    news_messages = ["🎮 오늘의 TOP 10 게임 뉴스! (테스트) 🎮\n"]
    for i, entry in enumerate(latest_entries):
        site_name = entry.link.split('/')[2].replace('www.', '')
        news_messages.append(f"*{i+1}위* | *{entry.title}* `({site_name})`\n<{entry.link}|자세히 보기>\n")
    
    send_to_slack("\n".join(news_messages))

if __name__ == "__main__":
    fetch_news()
