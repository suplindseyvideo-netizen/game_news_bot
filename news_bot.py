import feedparser
import requests
import os
import time

# 1. 현재 가장 안정적으로 작동하는 RSS 주소 목록으로 변경
RSS_URLS = [
    "http://rss.inven.co.kr/rss/news/webzine_total.xml", # 인벤 전체 뉴스 (안정적)
    "https://www.zdnet.co.kr/Include/RSS/zdnet_all.xml"  # 지디넷코리아 IT/게임 (안정적)
]

# 2. GitHub Secrets에서 슬랙 웹훅 URL 가져오기
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

def send_to_slack(message):
    """슬랙으로 메시지를 전송하는 함수"""
    if not SLACK_WEBHOOK_URL:
        print("에러: SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
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
        if feed.bozo:
            print(f"경고: {url} 피드를 파싱하는 데 문제가 있을 수 있습니다. (bozo=1)")
        all_entries.extend(feed.entries)
        
    if not all_entries:
        send_to_slack("모든 뉴스 사이트에서 새로운 기사를 가져오지 못했습니다.")
        return
        
    all_entries.sort(key=lambda x: x.get("published_parsed", time.gmtime(0)), reverse=True)
    latest_entries = all_entries[:10]

    news_messages = ["🎮 오늘의 TOP 10 게임/IT 뉴스! 🎮\n"]
    for i, entry in enumerate(latest_entries):
        site_name = entry.link.split('/')[2].replace('www.', '')
        news_messages.append(f"*{i+1}위* | *{entry.title}* `({site_name})`\n<{entry.link}|자세히 보기>\n")
    
    send_to_slack("\n".join(news_messages))

if __name__ == "__main__":
    fetch_news()
