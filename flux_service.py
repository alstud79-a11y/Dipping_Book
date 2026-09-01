import hashlib
import os
from pathlib import Path

from huggingface_hub import InferenceClient


BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "static" / "generated"
MODEL_ID = os.getenv("HF_FLUX_MODEL", "black-forest-labs/FLUX.1-schnell")


def generate_mood_image(book_key, visual_prompt):
    """Hugging Face FLUX로 분위기 이미지를 만들고 정적 파일 경로를 반환합니다."""
    token = (os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN", "")).strip()
    if not token:
        return None, "Hugging Face 토큰이 설정되지 않았습니다."

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    image_key = f"{book_key}|{visual_prompt}|v2"
    safe_name = hashlib.sha256(image_key.encode("utf-8")).hexdigest()[:20]
    filename = f"book_{safe_name}.png"
    output_path = GENERATED_DIR / filename

    if output_path.exists():
        return f"/static/generated/{filename}", None

    prompt = (
        f"{visual_prompt}. Editorial book mood artwork, cinematic composition, "
        "high quality, natural expressive face and anatomically correct hands when a "
        "person appears, no text, no letters, no typography, no logo, no watermark."
    )

    try:
        client = InferenceClient(
            provider="auto",
            api_key=token,
            timeout=120,
        )
        image = client.text_to_image(
            prompt,
            model=MODEL_ID,
            width=1024,
            height=768,
        )
        image.save(output_path, format="PNG")
        return f"/static/generated/{filename}", None
    except Exception as error:
        print(f"[FLUX 이미지 생성 오류] {error}")
        return None, "이미지 생성에 실패했습니다. Hugging Face 토큰과 무료 사용량을 확인해 주세요."
