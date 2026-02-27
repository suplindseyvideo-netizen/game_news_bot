import feedparser
import requests
import os
import time

# 1. 우선순위: 'site:' 검색을 통해 원하는 사이트의 뉴스만 가져오기
PRIMARY_URLS = [
    "https://news.google.com/rss/search?q=%EA%B2%8C%EC%9E%84+site:inven.co.kr&hl=ko&gl=KR&ceid=KR:ko",
    "https://news.google.com/rss/search?q=%EA%B2%8C%EC%9E%84+site:gamemeca.com&hl=ko&gl=KR&ceid=KR:ko",
    "https://news.google.com/rss/search?q=%EA%B2%8C%EC%9E%84+site:thisisgame.com&hl=ko&gl=KR&ceid=KR:ko",
]

# 2. 대안(Fallback): 우선순위가 실패했을 경우, '게임' 키워드로 일반 검색
FALLBACK_URLS = [
    "https://news.google.com/rss/search?q=%EA%B2%8C%EC%9E%84&hl=ko&gl=KR&ceid=KR:ko"
]

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

def get_entries_from_urls(urls):
    """주어진 URL 목록에서 모든 기사를 가져오는 함수"""
    all_entries = []
    for url in urls:
        print(f"{url} 에서 뉴스 가져오기 시도...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            if feed.entries:
                print(f"성공: {url} 에서 {len(feed.entries)}개의 기사를 찾았습니다.")
                all_entries.extend(feed.entries)
            else:
                print(f"경고: {url} 에서 기사를 찾지 못했습니다.")
        except requests.exceptions.RequestException as e:
            print(f"에러: {url} 에 접근하는 중 문제가 발생했습니다 - {e}")
    return all_entries

def fetch_news():
    """우선순위 -> 대안 순서로 뉴스를 가져와 슬랙으로 전송"""
    
    # 1. 우선순위 URL에서 기사 가져오기 시도
    print("--- 우선순위(Primary) URL에서 뉴스 검색을 시작합니다. ---")
    all_entries = get_entries_from_urls(PRIMARY_URLS)
    title = "🎮 오늘의 TOP 10 게임 뉴스! (Inven/TIG/GM) 🎮\n"

    # 2. 만약 우선순위에서 기사를 하나도 못 가져왔다면, 대안 URL에서 다시 시도
    if not all_entries:
        print("\n--- 우선순위 검색 실패. 대안(Fallback) URL에서 뉴스 검색을 시작합니다. ---")
        all_entries = get_entries_from_urls(FALLBACK_URLS)
        title = "⚠️[대안] 오늘의 TOP 10 게임 뉴스! (Google) 🎮\n"

    if not all_entries:
        send_to_slack("모든 방법(우선순위, 대안)으로도 뉴스를 가져오는 데 실패했습니다.")
        return
        
    all_entries.sort(key=lambda x: x.get("published_parsed", time.gmtime(0)), reverse=True)
    latest_entries = all_entries[:10]

    news_messages = [title]
    for i, entry in enumerate(latest_entries):
        source_name = entry.source.title if hasattr(entry, 'source') else "알 수 없는 출처"
        news_messages.append(f"*{i+1}위* | *{entry.title}* `({source_name})`\n<{entry.link}|자세히 보기>\n")

    send_to_slack("\n".join(news_messages))

if __name__ == "__main__":
    fetch_news()
