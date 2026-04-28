# 피싱 뉴스 수집

"""
여러 RSS 소스에서 매일 최신 피싱/보이스피싱 뉴스 수집
"""

import feedparser
import json
from datetime import datetime

RSS_SOURCES = [
    # 구글 뉴스 - 보이스피싱/스미싱
    "https://news.google.com/rss/search?q=보이스피싱+스미싱&gl=KR&hl=ko&ceid=KR:ko",
    # 구글 뉴스 - 금융사기
    "https://news.google.com/rss/search?q=금융사기+피싱+사기문자&gl=KR&hl=ko&ceid=KR:ko",
    # 구글 뉴스 - 택배/정부지원금 사기
    "https://news.google.com/rss/search?q=택배사기+정부지원금+사기문자&gl=KR&hl=ko&ceid=KR:ko",
    # 구글 뉴스 - 카카오톡/SNS 사기
    "https://news.google.com/rss/search?q=카카오톡사기+SNS사기+메신저피싱&gl=KR&hl=ko&ceid=KR:ko",
    # 구글 뉴스 - 대출사기/개인정보탈취
    "https://news.google.com/rss/search?q=대출사기+개인정보탈취+악성앱&gl=KR&hl=ko&ceid=KR:ko",
    # 금융감독원 보도자료 RSS
    "https://www.fss.or.kr/fss/rss/rssNewsView.do?rssType=press",
    # KISA 인터넷보호나라 보안공지 RSS
    "https://www.kisa.or.kr/rss/notice.do",
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
]


def collect(max_posts: int = 15) -> list[dict]:
    """여러 소스에서 최신 피싱 뉴스 수집 (소스별 균등 수집)"""
    print(f"[{datetime.now()}] 피해사례 수집 시작...")

    per_source = max(max_posts // len(RSS_SOURCES), 3)
    seen_titles = set()
    results = []

    for rss_url in RSS_SOURCES:
        try:
            feed = feedparser.parse(rss_url)
            count = 0
            for entry in feed.entries:
                if count >= per_source:
                    break
                title = entry.get("title", "").strip()
                if not title or title in seen_titles:
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
