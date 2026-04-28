"""Render 배포용 시작 스크립트: Flask 서버만 시작 (데이터는 GitHub Actions에서 수집)"""
import os
from dotenv import load_dotenv
from sender.kakao import create_skill_server

load_dotenv()
create_skill_server()
