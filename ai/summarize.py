# AI 요약 변환

"""
수집된 피싱 사례를 고령층 눈높이에 맞게 AI로 요약
"""

import re
import json
import os
from groq import Groq


def clean_text(text: str) -> str:
    """한자, 키릴 문자, 베트남어 등 비한글 제거 (이모지·숫자·문장부호 보존)"""
    # 한자 제거
    text = re.sub(r'[一-鿿㐀-䶿]+', '', text)
    # 키릴 문자 제거
    text = re.sub(r'[Ѐ-ӿ]+', '', text)
    # 베트남어 특수 발음 기호 포함 단어 제거
    text = re.sub(r'\b[a-zA-ZÀ-ỹ]*[àáâãèéêìíòóôõùúýăđơưạảấầẩẫậắặằẳẵẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĂĐƠƯ][a-zA-ZÀ-ỹ]*\b', '', text)
    # 한글 문장 중간에 끼어든 영문자만 제거 (숫자·이모지·문장부호는 유지)
    text = re.sub(r'(?<=[가-힣\s])[a-zA-Z]+(?=[가-힣\s])', '', text)
    # 연속 공백 정리
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


SYSTEM_PROMPT = """당신은 KBS 아나운서이자 국어 교사입니다. 대한민국 어르신들에게 피싱 피해 사례를 전달하는 안내문을 작성합니다.

[언어 규칙 — 절대 준수]
- 순수한 한국어만 사용합니다. 한자·영어·러시아어·베트남어·아랍어 등 모든 외국 문자 사용 금지.
- 외래어 단어 사용 금지 (예: cảnh giác, alert, phishing 등은 반드시 우리말로 대체).
- 번역 투 표현 금지 (예: "돈을하는", "피해를입은", "링크를클릭" 같은 띄어쓰기 오류 포함).
- 미완성 문장, 끊기는 문장 금지.

[문체 기준]
- KBS 표준어 방송 문체: 명확하고 간결하며 품위 있는 존댓말.
- 조사와 어미를 정확히 사용합니다 (예: "~에게", "~께서", "~하셨습니다").
- 같은 단어를 한 문단에 두 번 이상 반복하지 않습니다.
- 어르신이 이해하기 쉬운 쉬운 어휘를 선택합니다. 어려운 법률·기술 용어는 풀어 씁니다.

[올바른 표현 예시]
- 나쁜 예: "돈을하는 사기꾼" → 좋은 예: "돈을 갈취하는 사기범"
- 나쁜 예: "링크를클릭하면" → 좋은 예: "문자 속 주소를 누르면"
- 나쁜 예: "cảnh giác하고" → 좋은 예: "각별히 주의하시고"
- 나쁜 예: "피싱에 조심하세요" → 좋은 예: "사기 문자에 속지 않도록 주의하세요"
"""

PROOFREAD_PROMPT = """당신은 KBS 방송원고 교열 담당자입니다.
아래 텍스트의 내용은 절대 바꾸지 말고, 아나운서가 읽어도 어색하지 않도록 문법과 문체만 다듬어 주세요.

[교열 규칙]
- 조사 오류 수정 (예: "은는", "이가", "를을" 등 중복·혼용 제거)
- 어색한 어순을 자연스러운 한국어 어순으로 교정
- 문장이 끊기거나 흐름이 어색한 부분을 매끄럽게 연결
- 외국 문자·외래어가 남아 있으면 우리말로 대체
- 이모지(📢, ✅)와 출력 형식은 절대 변경하지 않음
- 내용 추가·삭제 금지, 교열만 수행
"""

USER_PROMPT_TEMPLATE = """아래 피싱 뉴스를 어르신도 쉽게 이해할 수 있는 안내문으로 작성해 주세요.

[작성 규칙]
- KBS 표준어 방송 문체, 존댓말 사용
- 같은 단어 반복 금지
- 전체 6줄 이내, 핵심 사실만 전달
- 예방법 1줄 반드시 포함
- 이모지는 📢, ✅ 각 1개씩만 사용

[출력 형식 — 반드시 이 형식 그대로]
📢 [한 줄 제목]

[사례 설명 2~3줄]

✅ 예방법: [한 줄]

---
제목: {title}
내용: {content}
"""


def proofread_korean(text: str) -> str:
    """1차 요약된 텍스트의 한국어 문법/어순 교정"""
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {"role": "system", "content": PROOFREAD_PROMPT},
            {"role": "user", "content": text}
        ]
    )
    return clean_text(completion.choices[0].message.content)


def summarize_case(title: str, content: str) -> str:
    """피싱 사례를 고령층 눈높이 메시지로 변환"""
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                title=title,
                content=content[:500]
            )}
        ]
    )
    result = clean_text(completion.choices[0].message.content)
    return proofread_korean(result)


MAX_SUMMARIZED = 30  # summarized.json 최대 보관 건수


def process_all(input_path: str = "data/raw_cases.json",
                output_path: str = "data/summarized.json"):
    """전체 사례 요약 처리 (기존 내용에 누적, 최대 MAX_SUMMARIZED건 유지)"""
    with open(input_path, encoding="utf-8") as f:
        cases = json.load(f)

    if not cases:
        print("[건너뜀] 신규 수집 기사 없음 → summarized.json 유지")
        return []

    existing = []
    try:
        with open(output_path, encoding="utf-8") as f:
            existing = json.load(f)
    except FileNotFoundError:
        pass

    existing_titles = {item["title"] for item in existing}
    new_results = []
    for case in cases:
        if case["title"] in existing_titles:
            continue
        print(f"  요약 중: {case['title'][:30]}...")
        summary = summarize_case(case["title"], case.get("content", ""))
        new_results.append({
            "title": case["title"],
            "date": case.get("date", ""),
            "summary": summary
        })

    combined = new_results + existing  # 신규를 앞에 추가
    combined = combined[:MAX_SUMMARIZED]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"[완료] 신규 {len(new_results)}개 추가, 총 {len(combined)}개 → {output_path}")
    return new_results


if __name__ == "__main__":
    process_all()
