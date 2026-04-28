# 프로젝트 주제
"오늘의 피싱 주의보" - 금융취약계층(고령층)을 위한 일일 피싱 알림 카카오 챗봇

매일 최신 피싱 뉴스 수집 → AI 요약 → 카카오 오픈빌더 챗봇으로 사용자에게 제공

# 결과물 예시
```
📢 오늘의 피싱 주의보

"국민건강보험 환급금이 있습니다" 문자를 받고
링크를 눌렀다가 개인정보가 털린 사례입니다.

✅ 예방법: 정부기관은 절대 문자로 링크를 보내지 않습니다.
```

# 시스템 흐름도
```
[데이터 수집]
구글뉴스 RSS / 금융감독원 RSS / KISA RSS
        ↓ (배포 시 자동 수집)
[AI 변환]
원문 → Groq(LLaMA 3.3) → 고령층 눈높이 한국어 요약
        ↓
[발송]
카카오 오픈빌더 챗봇 스킬 서버 (Render 호스팅)
```

# 폴더 구조
```
├── crawler/
│   └── collect.py        # RSS 피싱 뉴스 수집 (구글뉴스, 금감원, KISA)
├── ai/
│   └── summarize.py      # Groq AI 요약 변환
├── sender/
│   └── kakao.py          # 카카오 오픈빌더 스킬 서버 (Flask)
├── data/
│   ├── raw_cases.json    # 수집된 원문 (자동 생성)
│   └── summarized.json   # AI 요약 결과 (자동 생성)
├── db/
│   └── subscribers.json  # 구독자 정보
├── start_server.py        # Render 배포 진입점 (수집 + 서버 시작)
├── main.py                # 로컬 데이터 수집 전용
├── run.bat                # 로컬 실행용 배치 파일
├── update_data.bat        # 로컬 데이터 갱신용 배치 파일
├── Procfile               # Render 배포 설정
├── requirements.txt
└── .env                   # GROQ_API_KEY (git 제외)
```

# 환경변수
```
GROQ_API_KEY=your-groq-api-key
```
`.env` 파일에 저장. Render에는 환경변수로 직접 등록.

# 로컬 실행 (개발/테스트)
```powershell
# 가상환경 활성화
.venv\Scripts\activate

# 데이터 갱신 (필요 시)
python main.py

# 서버 실행 (Flask + cloudflared)
run.bat 더블클릭
```

# 배포 (Render - 프로덕션)
```
GitHub push → Render 자동 감지 → pip install → start_server.py 실행
```
- 배포 URL: `https://phishing-alert-project.onrender.com/skill`
- push 시 자동 재배포, 수동 조작 불필요
- 배포 시마다 최신 피싱 뉴스 자동 수집 후 서버 시작

# 카카오 오픈빌더 연동
1. https://i.kakao.com 접속
2. 스킬 → phishing-alert → URL: `https://phishing-alert-project.onrender.com/skill`
3. 블록별 발화 패턴 등록:
   - 오늘의 피싱 주의보 블록: `오늘사례`, `다음사례`, `예방팁`, `신고전화`, `처음으로`

# 챗봇 응답 구조
| 발화 | 응답 |
|------|------|
| `오늘사례`, `피싱`, `사례` 등 | 오늘의 피싱 사례 + 다음사례/예방팁/신고전화 버튼 |
| `다음사례` | 다음 사례로 이동 (날짜 기반 로테이션) |
| `예방팁` | 피싱 예방 핵심 팁 5가지 |
| `신고전화` | 112 / 1332 / 118 신고 안내 |
| 그 외 | 웰컴 메시지 + 메뉴 버튼 |

# 서비스 비용
| 서비스 | 비용 |
|--------|------|
| Groq API (LLaMA 3.3) | 무료 (일정 한도 내) |
| 카카오 오픈빌더 | 무료 |
| Render (Flask 서버) | 무료 (Free 플랜) |
| 카카오톡 채널 | 무료 |

> **참고:** Render 무료 플랜은 15분간 요청 없으면 서버가 잠듦.
> 잠든 상태의 첫 응답은 30~60초 소요될 수 있음.
