# 매일 자동 실행

"""
매일 오전 9시 자동 실행 스케줄러
pip install schedule
"""

import schedule
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.collect import collect
from ai.summarize import process_all


def daily_job():
    print("=" * 40)
    print("📢 오늘의 피싱 주의보 수집 시작")
    print("=" * 40)

    # 1. 크롤링
    collect(max_posts=3)

    # 2. AI 요약
    process_all()

    print("✅ 완료! 카카오 챗봇에서 확인 가능합니다.")


if __name__ == "__main__":
    # 매일 오전 9시 실행
    schedule.every().day.at("09:00").do(daily_job)

    print("스케줄러 시작 (매일 09:00 실행)")
    print("즉시 테스트하려면 daily_job()을 직접 호출하세요")

    # 즉시 1회 실행 후 스케줄 대기
    daily_job()

    while True:
        schedule.run_pending()
        time.sleep(60)