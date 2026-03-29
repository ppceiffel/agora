from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    app_name: str = "Agora"
    debug: bool = False
    secret_key: str

    # Database
    database_url: str

    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    # Claude API
    anthropic_api_key: str

    # Auth
    otp_expire_minutes: int = 10
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 jours


settings = Settings()
