import feedparser
import requests
import os
import time

# 1. 'site:' 검색을 활용해, 구글 뉴스를 통해 원하는 사이트의 기사만 가져오기
# "게임"이라는 키워드로 특정 사이트의 뉴스만 검색합니다.
# URL의 한글 부분은 URL 인코딩된 상태입니다. (예: %EA%B2%8C%EC%9E%84 = 게임)
RSS_URLS = [
    "https://news.google.com/rss/search?q=%EA%B2%8C%EC%9E%84+site:inven.co.kr&hl=ko&gl=KR&ceid=KR:ko",       # 인벤
    "https://news.google.com/rss/search?q=%EA%B2%8C%EC%9E%84+site:gamemeca.com&hl=ko&gl=KR&ceid=KR:ko",     # 게임메카
    "https://news.google.com/rss/search?q=%EA%B2%8C%EC%9E%84+site:thisisgame.com&hl=ko&gl=KR&ceid=KR:ko", # 디스이즈게임
]

# 2. GitHub Secrets에서 슬랙 웹훅 URL 가져오기
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

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
    """구글 'site:' 검색을 통해 특정 사이트들의 뉴스만 모아서 슬랙으로 전송"""
    all_entries = []
    for url in RSS_URLS:
        print(f"{url} 에서 뉴스 가져오기 시도...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            print(f"{url} 에서 {len(feed.entries)}개의 기사를 찾았습니다.")
            all_entries.extend(feed.entries)
        except requests.exceptions.RequestException as e:
            print(f"에러: {url} 에 접근하는 중 문제가 발생했습니다 - {e}")
    
    if not all_entries:
        send_to_slack("지정된 사이트들의 뉴스를 구글을 통해 가져오는 데 실패했습니다.")
        return
        
    # 모든 기사를 최신 순으로 정렬
    all_entries.sort(key=lambda x: x.get("published_parsed", time.gmtime(0)), reverse=True)
    latest_entries = all_entries[:10]

    news_messages = ["🎮 오늘의 TOP 10 게임 뉴스! (Inven/TIG/GM) 🎮\n"]
    for i, entry in enumerate(latest_entries):
        source_name = entry.source.title if hasattr(entry, 'source') else "알 수 없는 출처"
