@echo off
cd /d "%~dp0"

echo [1/2] Flask 서버 시작...
start "Flask 서버" cmd /k ".venv\Scripts\activate && python sender/kakao.py"

timeout /t 2 /nobreak >nul

echo [2/2] cloudflared 터널 시작...
start "cloudflared" cmd /k ".\cloudflared.exe tunnel --url http://localhost:5000"

echo.
echo 서버가 시작됐습니다.
echo cloudflared 창에서 https://xxxx.trycloudflare.com 주소를 확인하세요.
echo 카카오 오픈빌더에서 스킬 URL을 업데이트하세요.
pause
