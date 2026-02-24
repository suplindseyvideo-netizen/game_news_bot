import feedparser
import requests
import os
import time

# 1. 구독할 뉴스 사이트의 RSS 주소 목록
RSS_URLS = [
    "https://www.thisisgame.com/rss/",       # 디스이즈게임
    "https://www.gamemeca.com/rss/",         # 게임메카
    "http://rss.inven.co.kr/rss/news/webzine_total.xml" # 인벤
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
    """여러 RSS 피드에서 최신 뉴스를 모아 슬랙으로 전송하는 함수"""
    all_entries = []
    
    # 각 RSS 주소를 돌면서 모든 기사들을 all_entries 리스트에 추가
    for url in RSS_URLS:
        print(f"{url} 에서 뉴스 파싱 시작...")
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
        
    # 기사가 하나도 없는 경우
    if not all_entries:
        send_to_slack("새로운 뉴스가 없습니다.")
        return
        
    # 모든 기사를 최신 순으로 정렬 (published_parsed 기준)
    # published_parsed가 없는 경우를 대비하여 기본값 설정
    all_entries.sort(key=lambda x: x.get("published_parsed", time.gmtime(0)), reverse=True)
    
    # 정렬된 기사들 중에서 최신 5개만 선택
    latest_entries = all_entries[:5]

    news_messages = ["🎮 오늘의 최신 게임 뉴스! (종합) 🎮\n"]
    for entry in latest_entries:
        # 출처(사이트 이름)를 링크에서 추출
        site_name = entry.link.split('/')[2].replace('www.', '')
        news_messages.append(f"📰 *{entry.title}* `({site_name})`\n<{entry.link}|자세히 보기>\n")
    
    send_to_slack("\n".join(news_messages))

if __name__ == "__main__":
    fetch_news()
