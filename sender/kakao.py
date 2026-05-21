"""카카오 오픈빌더 챗봇 스킬 서버"""

import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "summarized.json")


def _load_cases() -> list:
    try:
        with open(_DATA_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def load_summary(offset: int = 0) -> str:
    cases = _load_cases()
    if cases:
        return cases[offset % len(cases)]["summary"]
    return "오늘은 새로운 피해사례가 없습니다. 항상 조심하세요! 💪"


def _parse_index(utterance: str) -> int:
    """'다음사례:3' 형식에서 인덱스 추출 (없으면 0)"""
    if ":" in utterance:
        try:
            return int(utterance.split(":", 1)[1])
        except ValueError:
            pass
    return 0


def build_message(summary: str, idx: int = 0) -> dict:
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": summary}}],
            "quickReplies": [
                {"label": "🆕 오늘의 피싱", "action": "message", "messageText": "오늘사례"},
                {"label": "➡️ 다음 사례", "action": "message", "messageText": f"다음사례:{idx + 1}"},
                {"label": "🛡️ 예방 팁", "action": "message", "messageText": "예방팁"},
                {"label": "📞 신고전화", "action": "message", "messageText": "신고전화"},
            ]
        }
    }


def build_welcome_message() -> dict:
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": "안녕하세요! 오늘의 피싱 주의보입니다 😊\n아래 버튼을 눌러주세요."}}],
            "quickReplies": [
                {"label": "📢 오늘의 피싱 사례", "action": "message", "messageText": "오늘사례"},
                {"label": "🛡️ 예방 팁", "action": "message", "messageText": "예방팁"},
                {"label": "📞 신고전화", "action": "message", "messageText": "신고전화"},
            ]
        }
    }


def build_hotline_message() -> dict:
    text = (
        "📞 피싱 피해 신고 연락처\n\n"
        "• 경찰청: 112\n"
        "• 금융감독원: 1332\n"
        "• 인터넷진흥원(해킹·스미싱): 118\n\n"
        "피해 발생 즉시 전화하세요!\n"
        "빠를수록 돈을 되찾을 확률이 높습니다."
    )
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
            "quickReplies": [
                {"label": "📢 오늘의 피싱 사례", "action": "message", "messageText": "오늘사례"},
                {"label": "🔙 처음으로", "action": "message", "messageText": "처음으로"},
            ]
        }
    }


def build_tips_message() -> dict:
    text = (
        "🛡️ 피싱 예방 핵심 팁\n\n"
        "1. 모르는 번호 전화는 받지 마세요\n"
        "2. 문자 속 링크는 절대 누르지 마세요\n"
        "3. 정부기관은 링크로 개인정보를 요구하지 않습니다\n"
        "4. 가족에게 돈을 보내달라는 문자는 먼저 전화로 확인하세요\n"
        "5. 의심되면 즉시 112 또는 1332에 신고하세요"
    )
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
            "quickReplies": [
                {"label": "📢 오늘의 피싱 사례", "action": "message", "messageText": "오늘사례"},
                {"label": "📞 신고전화", "action": "message", "messageText": "신고전화"},
                {"label": "🔙 처음으로", "action": "message", "messageText": "처음으로"},
            ]
        }
    }


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


@app.route("/skill", methods=["POST"])
def skill():
    body = request.get_json(silent=True) or {}
    utterance = body.get("userRequest", {}).get("utterance", "").strip()

    if utterance in ("신고전화", "신고", "전화"):
        return jsonify(build_hotline_message())

    if utterance == "예방팁":
        return jsonify(build_tips_message())

    if utterance.startswith("다음사례"):
        idx = _parse_index(utterance)
        return jsonify(build_message(load_summary(idx), idx))

    if utterance in ("오늘사례", "처음으로", "오늘의피싱") or any(
        kw in utterance for kw in ["피싱", "사기", "주의보", "사례", "알려줘"]
    ):
        return jsonify(build_message(load_summary(0), 0))

    return jsonify(build_welcome_message())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"카카오 스킬 서버 시작: http://0.0.0.0:{port}/skill")
    app.run(host="0.0.0.0", port=port)
