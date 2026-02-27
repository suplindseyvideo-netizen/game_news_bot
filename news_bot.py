import feedparser
import requests
import os
import time

# 1. 구글 뉴스 RSS 주소 사용 (키워드: '게임')
# 가장 안정적이고, 절대 차단되지 않는 방법입니다.
RSS_URLS = [
    "https://news.google.com/rss/search?q=%EA%B2%8C%EC%9E%84&hl=ko&gl=KR&ceid=KR:ko"
]

# 2. GitHub Secrets에서 슬랙 웹훅 URL 가져오기
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

# 3. 브라우저인 척 위장하기 위한 헤더 정보
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def send_to_slack(message):
    """슬랙으로 메시지를 전송하는 함수"""
    payload = {"text": message}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        print("슬랙 메시지 전송 성공!")
    except requests.exceptions.RequestException as e:
        print(f"에러: 슬랙 메시지 전송 실패 - {e}")

def fetch_news():
    """구글 뉴스 RSS에서 최신 기사 10개를 가져와 슬랙으로 전송"""
    all_entries = []
    
    for url in RSS_URLS:
        print(f"{url} 에서 뉴스 가져오기 시도...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.content)

            if not feed.entries:
                print(f"경고: {url} 에서 기사를 찾지 못했습니다.")
            else:
                print(f"{url} 에서 {len(feed.entries)}개의 기사를 찾았습니다.")
                all_entries.extend(feed.entries)

        except requests.exceptions.RequestException as e:
            print(f"에러: {url} 에 접근하는 중 문제가 발생했습니다 - {e}")
    
    if not all_entries:
        send_to_slack("구글 뉴스에서 기사를 가져오지 못했습니다. 일시적인 문제일 수 있습니다.")
        return
        
    # 구글 뉴스는 시간순 정렬이 이미 잘 되어 있으므로, 그대로 사용
    latest_entries = all_entries[:10]

    news_messages = ["🎮 오늘의 TOP 10 게임 뉴스! (Google News) 🎮\n"]
    for i, entry in enumerate(latest_entries):
        # 구글 뉴스 RSS는 출처(source) 정보를 제공합니다.
        source_name = entry.source.title if hasattr(entry, 'source') else "알 수 없는 출처"
        news_messages.append(f"*{i+1}위* | *{entry.title}* `({source_name})`\n<{entry.link}|자세히 보기>\n")

    send_to_slack("\n".join(news_messages))

if __name__ == "__main__":
    if not SLACK_WEBHOOK_URL:
        print("치명적 에러: SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
    else:
        fetch_news()
