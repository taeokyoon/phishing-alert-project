"""Render 배포용 시작 스크립트: 데이터 수집 후 Flask 서버 실행"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 데이터 파일 없을 때만 수집 (배포 시 최초 1회)
if not os.path.exists("data/summarized.json"):
    from crawler.collect import collect
    from ai.summarize import process_all
    collect(max_posts=15)
    process_all()

from sender.kakao import create_skill_server
create_skill_server()
