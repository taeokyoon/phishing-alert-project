@echo off
cd /d "%~dp0"

echo 피싱 데이터 수집 및 AI 요약 시작...
.venv\Scripts\activate && python main.py

echo.
echo 완료! 이제 run.bat을 실행하세요.
pause
