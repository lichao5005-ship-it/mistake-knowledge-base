from openai import OpenAI
from app.shared.config import settings

client = OpenAI(
    api_key=settings.qwen_api_key,
    base_url=settings.qwen_api_base,
)


def call_qwen_vision(prompt: str, image_data: bytes, model: str | None = None) -> str:
    import base64

    b64 = base64.b64encode(image_data).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{b64}"
    resp = client.chat.completions.create(
        model=model or settings.qwen_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content or ""


def call_qwen_text(prompt: str, model: str | None = None) -> str:
    resp = client.chat.completions.create(
        model=model or settings.qwen_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content or ""
