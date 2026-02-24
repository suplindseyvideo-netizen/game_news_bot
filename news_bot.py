import requests
import os

# GitHub Secrets에서 슬랙 웹훅 URL 가져오기
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

def send_to_slack(message):
    """슬랙으로 메시지를 전송하는 함수"""
    if not SLACK_WEBHOOK_URL:
        print("에러: SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
        return

    print("슬랙으로 테스트 메시지를 전송합니다...")
    payload = {"text": message}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("슬랙 메시지 전송 성공!")
    except requests.exceptions.RequestException as e:
        print(f"에러: 슬랙 메시지 전송 실패 - {e}")

# 프로그램이 시작되면 이 부분을 실행
if __name__ == "__main__":
    # 뉴스 크롤링 로직 없이, 무조건 성공 메시지를 보냅니다.
    send_to_slack("🚀 최종 테스트 성공! 🚀\n이제 슬랙 연동이 완벽하게 작동합니다. 코드를 원래대로 되돌려주세요!")

