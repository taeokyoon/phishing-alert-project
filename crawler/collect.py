# 피싱 뉴스 수집

"""
여러 RSS 소스에서 매일 최신 피싱/보이스피싱 뉴스 수집
"""

import feedparser
import json
from datetime import datetime, timezone, timedelta
import email.utils

# 제목에 반드시 포함돼야 하는 핵심 키워드
CORE_KEYWORDS = [
    "피싱", "보이스피싱", "스미싱", "파밍", "메신저피싱",
    "사기문자", "사기 문자", "사기전화", "사기 전화",
    "금융사기", "대출사기", "택배사기", "전화사기",
    "전화금융사기", "문자사기", "카카오톡사기",
    "정부지원금 사기", "정부지원금사기",
    "악성앱", "악성 앱", "랜섬웨어",
    "개인정보 탈취", "개인정보탈취",
    "불법 대출", "불법대출", "스팸문자",
    "사기 피해", "사기피해", "피싱 피해",
    "해킹 피해", "해킹피해", "개인정보 유출",
]

SECONDARY_TITLE_KEYWORDS = ["사기", "피해", "사칭", "해킹", "피싱"]


def is_phishing_related(title: str, content: str) -> bool:
    # 1단계: 제목에 핵심 키워드
    if any(kw in title for kw in CORE_KEYWORDS):
        return True
    # 2단계: 제목에 일반 사기 관련어 + 내용에 핵심 키워드
    if any(kw in title for kw in SECONDARY_TITLE_KEYWORDS):
        if any(kw in content for kw in CORE_KEYWORDS):
            return True
    return False

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
    # 연합뉴스 - 사회 (보조)
    "https://www.yna.co.kr/rss/society.xml",
    # 매일경제 - 사회 (보조)
    "https://www.mk.co.kr/rss/30100041/",
    # KISA 인터넷보호나라 보안공지 RSS
    "https://www.kisa.or.kr/rss/notice.do",
]


MAX_AGE_DAYS = 3   # 이 기간보다 오래된 기사는 제외


def parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        t = email.utils.parsedate_to_datetime(date_str)
        return t.astimezone(timezone.utc)
    except Exception:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str[:19], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def collect(max_posts: int = 15) -> list[dict]:
    """여러 소스에서 최신 피싱 뉴스 수집 (소스별 균등 수집, 3일 이내만)"""
    print(f"[{datetime.now()}] 피해사례 수집 시작...")
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)

    per_source = max(max_posts // len(RSS_SOURCES), 3)
    seen_titles = set()
    seen_links = set()
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
                link = entry.get("link", "")
                if not title or title in seen_titles or (link and link in seen_links):
                    continue
                pub_date = parse_date(entry.get("published", ""))
                if pub_date and pub_date < cutoff:
                    print(f"  ⏭️ 오래된 기사 제외: {title[:30]}... ({entry.get('published', '')[:10]})")
                    continue
                if not is_phishing_related(title, content):
                    continue
                seen_titles.add(title)
                if link:
                    seen_links.add(link)
                results.append({
                    "title": title,
                    "link": link,
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
