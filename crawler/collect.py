# 피싱 뉴스 수집

"""
여러 RSS 소스에서 매일 최신 피싱/보이스피싱 뉴스 수집
"""

import feedparser
import json
from datetime import datetime

# 제목에 반드시 포함돼야 하는 핵심 키워드
CORE_KEYWORDS = [
    "피싱", "보이스피싱", "스미싱", "파밍",
    "사기문자", "사기전화", "사기 문자", "사기 전화",
    "메신저피싱", "금융사기", "대출사기", "택배사기",
    "개인정보 탈취", "개인정보탈취", "악성앱", "악성 앱",
    "카카오톡 사기", "카카오톡사기", "계좌이체 사기",
    "정부지원금 사기", "사칭 문자", "사칭문자",
    "피해 주의", "피해주의", "사기 피해", "사기피해",
    "보안 경고", "보안경고", "해킹 피해", "해킹피해",
    "랜섬웨어", "스팸문자", "불법 대출", "불법대출",
]


def is_phishing_related(title: str, content: str) -> bool:
    # 제목에 핵심 키워드가 있어야 통과
    return any(kw in title for kw in CORE_KEYWORDS)

RSS_SOURCES = [
    # 구글 뉴스 - 보이스피싱/스미싱 (로컬 환경에서 작동)
    "https://news.google.com/rss/search?q=보이스피싱+스미싱&gl=KR&hl=ko&ceid=KR:ko",
    "https://news.google.com/rss/search?q=금융사기+피싱+사기문자&gl=KR&hl=ko&ceid=KR:ko",
    "https://news.google.com/rss/search?q=택배사기+정부지원금+사기문자&gl=KR&hl=ko&ceid=KR:ko",
    "https://news.google.com/rss/search?q=카카오톡사기+SNS사기+메신저피싱&gl=KR&hl=ko&ceid=KR:ko",
    "https://news.google.com/rss/search?q=대출사기+개인정보탈취+악성앱&gl=KR&hl=ko&ceid=KR:ko",
    # 연합뉴스 - 사회
    "https://www.yna.co.kr/rss/society.xml",
    # 연합뉴스 - 경제
    "https://www.yna.co.kr/rss/economy.xml",
    # 매일경제 - 사회
    "https://www.mk.co.kr/rss/30100041/",
    # 매일경제 - 경제
    "https://www.mk.co.kr/rss/50400012/",
    # 한국경제 - 전체
    "https://www.hankyung.com/feed/all-news",
    # 금융감독원 보도자료 RSS
    "https://www.fss.or.kr/fss/rss/rssNewsView.do?rssType=press",
    # KISA 인터넷보호나라 보안공지 RSS
    "https://www.kisa.or.kr/rss/notice.do",
]


def collect(max_posts: int = 15) -> list[dict]:
    """여러 소스에서 최신 피싱 뉴스 수집 (소스별 균등 수집)"""
    print(f"[{datetime.now()}] 피해사례 수집 시작...")

    per_source = max(max_posts // len(RSS_SOURCES), 3)
    seen_titles = set()
    results = []

    USER_AGENT = "Mozilla/5.0 (compatible; PhishingAlertBot/1.0)"

    for rss_url in RSS_SOURCES:
        try:
            feed = feedparser.parse(rss_url, agent=USER_AGENT)
            print(f"  [{rss_url[:40]}] 상태: {feed.status if hasattr(feed, 'status') else 'N/A'}, 항목 수: {len(feed.entries)}")
            count = 0
            for entry in feed.entries:
                if count >= per_source:
                    break
                title = entry.get("title", "").strip()
                content = entry.get("summary", "")
                if not title or title in seen_titles:
                    continue
                if not is_phishing_related(title, content):
                    continue
                seen_titles.add(title)
                results.append({
                    "title": title,
                    "link": entry.get("link", ""),
                    "date": entry.get("published", ""),
                    "content": entry.get("summary", "")
                })
                print(f"  ✅ 수집: {title[:30]}...")
                count += 1
        except Exception as e:
            print(f"  ⚠️ {rss_url[:40]} 수집 실패: {e}")

    results = results[:max_posts]
    print(f"  총 {len(results)}개 뉴스 수집")

    with open("data/raw_cases.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[완료] {len(results)}개 저장 → data/raw_cases.json")
    return results


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    collect(max_posts=15)
