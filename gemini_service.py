import os
import json

import requests


def _simple_fallback(text):
    return "쉬운 글을 만들지 못했습니다. 잠시 후 다시 눌러 주세요."


def make_easy_text(text):
    result = make_book_preview(text)
    return result["easy_text"], result["used_api"]


def make_book_preview(text):
    """책 소개를 쉬운 글과 FLUX용 영어 프롬프트로 변환합니다."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    if not api_key:
        return {
            "easy_text": _simple_fallback(text),
            "visual_prompt": (
                "A warm editorial illustration inspired by reading a meaningful book, "
                "soft natural light, calm atmosphere, no text, no letters, no book cover"
            ),
            "used_api": False,
        }

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model_name}:generateContent"
    )
    prompt = (
        "다음 책 소개를 분석해서 JSON으로만 답하세요.\n"
        '1. "easy_text": 초등학교 저학년도 이해할 수 있는 쉬운 한국어 3~4문장. '
        "한 문장에는 한 가지 내용만 담고, 문장을 짧게 쓰세요. "
        "어려운 한자어, 전문용어, 긴 수식어는 쉬운 일상말로 바꾸세요. "
        "책 제목과 핵심 내용은 유지하고 새로운 내용은 만들지 마세요.\n"
        '2. "visual_prompt": 책의 분위기를 표현하는 FLUX 이미지 생성용 영어 프롬프트. '
        "책 내용에 사람이 어울리면 자연스러운 표정과 얼굴이 보이는 인물을 포함하세요. "
        "얼굴, 손, 신체 비율이 어색하지 않게 하고 글자와 로고는 넣지 마세요. "
        "장면과 색감이 책의 분위기와 어울리도록 한 문단으로 작성하세요.\n\n"
        f"책 소개: {text}"
    )
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    try:
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            json=body,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        parsed = json.loads(raw_text)
        if isinstance(parsed, list):
            if not parsed:
                raise ValueError("Gemini 응답이 빈 목록입니다.")
            parsed = parsed[0]
        if not isinstance(parsed, dict):
            raise TypeError("Gemini 응답이 JSON 객체 형식이 아닙니다.")
        easy_text = str(parsed.get("easy_text", "")).strip()
        visual_prompt = str(parsed.get("visual_prompt", "")).strip()
        if not easy_text or not visual_prompt:
            raise ValueError("Gemini 응답에 필요한 항목이 없습니다.")
        return {
            "easy_text": easy_text,
            "visual_prompt": visual_prompt,
            "used_api": True,
        }
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
        print(f"[Gemini 쉬운 글 생성 오류] {error}")
        return {
            "easy_text": _simple_fallback(text),
            "visual_prompt": (
                "A natural editorial illustration inspired by a meaningful book, "
                "warm daylight, expressive human character when appropriate, "
                "realistic face and hands, balanced composition, no text or logo"
            ),
            "used_api": False,
        }
