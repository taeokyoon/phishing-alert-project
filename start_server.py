"""Render 배포용 시작 스크립트: 데이터 수집 후 Flask 서버 실행"""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)

from crawler.collect import collect
from ai.summarize import process_all
from sender.kakao import create_skill_server

collect(max_posts=15)
process_all()
create_skill_server()
