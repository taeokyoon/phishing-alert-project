# AI 요약 변환

"""
수집된 피싱 사례를 고령층 눈높이에 맞게 AI로 요약
"""

import re
import json
import os
from groq import Groq


def clean_text(text: str) -> str:
    """한자, 키릴 문자 등 비한글 제거 (이모지·숫자·문장부호 보존)"""
    # 한자 제거
    text = re.sub(r'[一-鿿㐀-䶿]+', '', text)
    # 키릴 문자 제거
    text = re.sub(r'[Ѐ-ӿ]+', '', text)
    # 한글 문장 중간에 끼어든 영문자만 제거 (숫자·이모지·문장부호는 유지)
    text = re.sub(r'(?<=[가-힣\s])[a-zA-Z]+(?=[가-힣\s])', '', text)
    # 연속 공백 정리
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


SYSTEM_PROMPT = """당신은 대한민국 국민들을 위한 피싱 예방 안내문 작성 전문가입니다.
반드시 공손하고 어색하지 않은 잘 들어맞는 한국어 문장으로만 작성하세요.

[절대 금지]
- 한자, 영어, 러시아어 등 외국 문자 일절 사용 금지
- 어색한 번역 투 표현 금지 (예: "돈을하는", "피싱에eware", "문자가 많이 돌아고 있습니다" 등)
- 미완성 문장 금지

[올바른 표현 예시]
- 나쁜 예: "돈을하는 사기꾼" → 좋은 예: "돈을 갈취하는 피싱범"
- 나쁜 예: "лич정보를 묻는" → 좋은 예: "개인정보를 요구하는"
- 나쁜 예: "피싱에eware하세요" → 좋은 예: "피싱 사기를 조심하세요"
- 나쁜 예: "돈을 받는다는 속임수" → 좋은 예: "돈을 돌려준다며 속이는 수법"
"""

PROOFREAD_PROMPT = """당신은 한국어 교정 전문가입니다.
아래 텍스트의 내용은 절대 바꾸지 말고, 문법과 어순만 자연스럽게 다듬어주세요.

[교정 규칙]
- 조사 중복 제거 (예: "는에" → "에", "이가" → "가")
- 어색한 어순 교정
- 문장 흐름이 끊기는 부분 자연스럽게 연결
- 이모지, 출력 형식(📢, ✅) 그대로 유지
- 내용 추가/삭제 금지, 오직 교정만
"""

USER_PROMPT_TEMPLATE = """아래 피싱 뉴스를 어르신도 이해할 수 있는 자연스러운 한국어로 변환해주세요.

[작성 규칙]
- 자연스러운 한국어 문장 사용
- 작성 된 텍스트를 다시 한 번 자연스럽고 어색하지 않은 문맥으로 다듬을 것
- 반복적인 단어 사용 금지 (ex. 요즘은 금융범죄가 많습니다. 요즘은 고유가 지원... )
- 7줄 이내로 핵심만
- 예방법 1줄 포함
- 이모지 1-2개 사용
- 말투: 공손한 어법 사용
- 날짜는 스크롤된 날짜를 기반으로 함

[출력 형식]
📢 [한 줄 제목]

[사례 설명 1-2줄]

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


def process_all(input_path: str = "data/raw_cases.json",
                output_path: str = "data/summarized.json"):
    """전체 사례 요약 처리"""
    with open(input_path, encoding="utf-8") as f:
        cases = json.load(f)

    results = []
    for case in cases:
        print(f"  요약 중: {case['title'][:30]}...")
        summary = summarize_case(case["title"], case.get("content", ""))
        results.append({
            "title": case["title"],
            "date": case.get("date", ""),
            "summary": summary
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[완료] {len(results)}개 요약 저장 → {output_path}")
    return results


if __name__ == "__main__":
    process_all()
