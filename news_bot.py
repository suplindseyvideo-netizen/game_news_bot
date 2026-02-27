import feedparser
import requests
import os
import time

# 1. 구독할 뉴스 사이트의 RSS 주소 목록
RSS_URLS = [
    "http://rss.inven.co.kr/rss/news/webzine_total.xml", # 인벤 전체 뉴스
    "https://www.zdnet.co.kr/Include/RSS/zdnet_all.xml",  # 지디넷코리아 IT/게임
    "https://www.thisisgame.com/rss/", # 디스이즈게임
    "https://www.gamemeca.com/rss/",   # 게임메카
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
    """여러 RSS 피드를 '브라우저처럼' 요청해서 뉴스를 모으고, 최신순 상위 10개를 슬랙으로 전송"""
    all_entries = []
    
    for url in RSS_URLS:
        print(f"{url} 에서 뉴스 가져오기 시도...")
        try:
            # 1. requests로 먼저 데이터를 가져온다 (브라우저처럼!)
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status() # 실패하면 에러 발생
            
            # 2. 가져온 텍스트 데이터를 feedparser로 파싱한다
            feed = feedparser.parse(response.content)

            if feed.bozo:
                print(f"경고: {url} 피드 형식에 문제가 있을 수 있습니다. (bozo=1)")

            if not feed.entries:
                print(f"경고: {url} 에서 기사를 찾지 못했습니다.")
            else:
                print(f"{url} 에서 {len(feed.entries)}개의 기사를 찾았습니다.")
                all_entries.extend(feed.entries)

        except requests.exceptions.RequestException as e:
            print(f"에러: {url} 에 접근하는 중 문제가 발생했습니다 - {e}")
    
    if not all_entries:
        send_to_slack("모든 뉴스 사이트에서 새로운 기사를 가져오지 못했습니다. RSS 주소가 변경되었거나, 사이트에서 봇을 차단했을 수 있습니다.")
        return
        
    all_entries.sort(key=lambda x: x.get("published_parsed", time.gmtime(0)), reverse=True)
    latest_entries = all_entries[:10]

    news_messages = ["🎮 오늘의 TOP 10 게임 뉴스! (최종) 🎮\n"]
    for i, entry in enumerate(latest_entries):
        try:
            site_name = entry.link.split('/')[2].replace('www.', '')
            news_messages.append(f"*{i+1}위* | *{entry.title}* `({site_name})`\n<{entry.link}|자세히 보기>\n")
        except (IndexError, AttributeError) as e:
            print(f"경고: 기사 정보를 파싱하는 데 실패했습니다 - {e}")

    send_to_slack("\n".join(news_messages))

if __name__ == "__main__":
    if not SLACK_WEBHOOK_URL:
        print("치명적 에러: SLACK_WEBHOOK_URL이 설정되지 않았습니다. GitHub Secrets를 확인해주세요.")
    else:
        fetch_news()
