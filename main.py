"""로컬 데이터 수집 전용 (GitHub Actions에서도 사용)"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.collect import collect
from ai.summarize import process_all

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def run():
    load_dotenv()
    os.makedirs(_DATA_DIR, exist_ok=True)
    collect(max_posts=15)
    process_all(
        input_path=os.path.join(_DATA_DIR, "raw_cases.json"),
        output_path=os.path.join(_DATA_DIR, "summarized.json"),
    )
    print("완료!")


if __name__ == "__main__":
    run()
