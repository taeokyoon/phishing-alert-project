# 재가동 순서

## 1. 가상환경 활성화
```powershell
.venv\Scripts\activate
```

## 2. 피싱 사례 수집 + AI 요약 (데이터 갱신 시)
```powershell
python main.py
```

## 3. Flask 서버 실행 (새 터미널)
```powershell
.venv\Scripts\activate
python sender/kakao.py
```

## 4. cloudflared 터널 실행 (새 터미널)
```powershell
.\cloudflared.exe tunnel --url http://localhost:5000
```
→ 출력된 `https://xxxx.trycloudflare.com` 주소 복사

## 5. 카카오 오픈빌더 스킬 URL 업데이트
1. https://i.kakao.com 접속
2. 오늘의 피싱 주의보 → 스킬 → phishing-alert
3. URL을 새 주소로 변경: `https://xxxx.trycloudflare.com/skill`
4. 저장

## 6. 배포
---

> **주의:** cloudflared 임시 URL은 터미널을 닫을 때마다 바뀝니다.
> 매번 오픈빌더에 새 URL을 등록해야 합니다.
