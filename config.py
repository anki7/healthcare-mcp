from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    fhir_base_url: str = "https://hapi.fhir.org/baseR4"

    class Config:
        env_file = ".env"

settings = Settings()
