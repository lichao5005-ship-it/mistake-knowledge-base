from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    qwen_api_key: str = ""
    qwen_api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen3.7-plus"
    secret_key: str = "dev-secret-key"
    database_url: str = "sqlite:///./mistake.db"
    upload_dir: str = "./app/static/uploads"
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
