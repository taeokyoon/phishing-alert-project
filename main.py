import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.collect import collect
from ai.summarize import process_all


def run():
    load_dotenv()
    os.makedirs("data", exist_ok=True)
    collect(max_posts=15)
    process_all()
    print("완료! sender/kakao.py를 실행해 카카오 스킬 서버를 시작하세요.")


if __name__ == "__main__":
    run()
