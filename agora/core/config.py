from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    app_name: str = "Agora"
    debug: bool = False
    secret_key: str = "dev-secret-change-in-production"

    # Database
    database_url: str = "sqlite:///./agora_dev.db"

    # Twilio — optionnel en dev (si absent, l'OTP est loggué dans la console)
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_phone_number: str | None = None

    # Claude API — optionnel en dev (le pipeline AI ne tourne pas sans)
    anthropic_api_key: str | None = None

    # CORS — URL du frontend en production
    frontend_url: str = "http://localhost:3000"

    # Admin — protège les endpoints /admin/*
    admin_secret: str | None = None

    # Auth
    otp_expire_minutes: int = 10
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 jours

    @property
    def twilio_enabled(self) -> bool:
        return all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number])


settings = Settings()
