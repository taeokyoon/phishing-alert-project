"""로컬 개발용 서버 실행 스크립트 (Render는 Procfile의 gunicorn 사용)"""
import os
from dotenv import load_dotenv

load_dotenv()

from sender.kakao import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
