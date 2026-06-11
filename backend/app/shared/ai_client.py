from openai import OpenAI

from app.shared.config import settings


def _get_client() -> OpenAI:
    """懒初始化 OpenAI 客户端，避免无 API key 时导入失败"""
    return OpenAI(
        api_key=settings.qwen_api_key,
        base_url=settings.qwen_api_base,
    )


def call_qwen_vision(prompt: str, image_data: bytes, model: str | None = None) -> str:
    """调用 Qwen 多模态模型，图片以 base64 格式传入"""
    import base64

    client = _get_client()
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
    """纯文本调用（用于出题、分析等不需要图片的场景）"""
    client = _get_client()
    resp = client.chat.completions.create(
        model=model or settings.qwen_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content or ""
