"""여러 RSS 소스에서 매일 최신 피싱/보이스피싱 뉴스 수집"""

import feedparser
import json
import os
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import email.utils

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# 제목에 반드시 포함돼야 하는 핵심 키워드 (일반 소비자 대상 피싱/사기)
CORE_KEYWORDS = [
    "피싱", "보이스피싱", "스미싱", "파밍", "메신저피싱",
    "사기문자", "사기 문자", "사기전화", "사기 전화",
    "금융사기", "대출사기", "택배사기", "전화사기",
    "전화금융사기", "문자사기", "카카오톡사기",
    "정부지원금 사기", "정부지원금사기",
    "개인정보 탈취", "개인정보탈취",
    "불법 대출", "불법대출", "스팸문자",
    "사기 피해", "사기피해", "피싱 피해",
    "해킹 피해", "해킹피해", "개인정보 유출",
]

# 제목에 있을 때 내용까지 확인하는 보조 키워드
# (단독으로는 기술 보안 기사일 수 있어 내용에 핵심 키워드가 있어야 통과)
SECONDARY_TITLE_KEYWORDS = ["사기", "피해", "사칭", "해킹", "피싱", "랜섬웨어", "악성앱", "악성 앱"]


def is_phishing_related(title: str, content: str) -> bool:
    # 1단계: 제목에 핵심 키워드
    if any(kw in title for kw in CORE_KEYWORDS):
        return True
    # 2단계: 제목에 보조 키워드 + 내용에 핵심 키워드
    if any(kw in title for kw in SECONDARY_TITLE_KEYWORDS):
        if any(kw in content for kw in CORE_KEYWORDS):
            return True
    return False


MAX_AGE_DAYS = 7   # 이 기간보다 오래된 기사는 제외


def _google_news_url(query_ko: str) -> str:
    """최근 7일 기사만 반환하는 구글뉴스 RSS URL 생성"""
    week_ago = (datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)).strftime("%Y-%m-%d")
    q = quote(f"{query_ko} after:{week_ago}")
    return f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"

STATIC_RSS_SOURCES = [
    # 데일리시큐 - 보안 전문 매체
    "https://www.dailysecu.com/rss/allArticle.xml",
    # 연합뉴스 - 사회 (보이스피싱 사건 기사 포함)
    "https://www.yna.co.kr/rss/society.xml",
    # 연합뉴스 - 경제 (금융사기 기사 포함)
    "https://www.yna.co.kr/rss/economy.xml",
    # 뉴시스 - 사회 (금융사기 기사 포함)
    "https://newsis.com/RSS/society.xml",
]

_GOOGLE_NEWS_QUERIES = [
    "보이스피싱 스미싱",
    "전화금융사기 피해",
]


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


def _title_fingerprint(title: str) -> str:
    """중복 판별용: 특수문자·공백 제거 후 앞 18자"""
    return re.sub(r"[^\w가-힣]", "", title)[:18]


def collect(max_posts: int = 15) -> list[dict]:
    """여러 소스에서 최신 피싱 뉴스 수집 (소스별 균등 수집, 7일 이내만)"""
    print(f"[{datetime.now()}] 피해사례 수집 시작...")
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)

    rss_sources = STATIC_RSS_SOURCES + [_google_news_url(q) for q in _GOOGLE_NEWS_QUERIES]
    per_source = max(max_posts // len(rss_sources), 3)
    seen_titles = set()
    seen_fingerprints = set()
    seen_links = set()
    results = []

    USER_AGENT = "Mozilla/5.0 (compatible; PhishingAlertBot/1.0)"

    for rss_url in rss_sources:
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
                fp = _title_fingerprint(title)
                if not title or title in seen_titles or fp in seen_fingerprints or (link and link in seen_links):
                    continue
                pub_date = parse_date(entry.get("published", ""))
                if pub_date and pub_date < cutoff:
                    print(f"  ⏭️ 오래된 기사 제외: {title[:30]}... ({entry.get('published', '')[:10]})")
                    continue
                if not is_phishing_related(title, content):
                    continue
                seen_titles.add(title)
                seen_fingerprints.add(fp)
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

    os.makedirs(_DATA_DIR, exist_ok=True)
    out_path = os.path.join(_DATA_DIR, "raw_cases.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[완료] {len(results)}개 저장 → {out_path}")
    return results


if __name__ == "__main__":
    collect(max_posts=15)
