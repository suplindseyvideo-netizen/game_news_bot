import feedparser
import requests
import os

# 1. IT/게임 뉴스 RSS 주소 (원하는 다른 뉴스로 변경 가능)
# 예시: 인벤 전체 뉴스
RSS_URL = "http://rss.inven.co.kr/rss/news/webzine_total.xml"

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
        response.raise_for_status()  # 요청이 실패하면 예외 발생
        print("슬랙 메시지 전송 성공!")
    except requests.exceptions.RequestException as e:
        print(f"에러: 슬랙 메시지 전송 실패 - {e}")

def fetch_news():
    """RSS 피드에서 최신 뉴스를 가져와 슬랙으로 전송하는 함수"""
    print(f"{RSS_URL} 에서 뉴스 파싱 시작...")
    feed = feedparser.parse(RSS_URL)
    
    # 최신 뉴스 5개만 선택
    latest_entries = feed.entries[:5]
    
    if not latest_entries:
        send_to_slack("새로운 뉴스가 없습니다.")
        return

    news_messages = ["🎮 오늘의 최신 게임 뉴스! 🎮\n"]
    for entry in latest_entries:
        news_messages.append(f"📰 *{entry.title}*\n<{entry.link}|자세히 보기>\n")
    
    send_to_slack("\n".join(news_messages))

if __name__ == "__main__":
    fetch_news()

