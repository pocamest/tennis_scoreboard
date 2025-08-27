from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    db_url: str
    db_echo: bool = False

    base_dir: Path = BASE_DIR
    template_dir: Path = base_dir / 'app' / 'templates'
    static_dir: Path = base_dir / 'app' / 'static'

    static_url: str = '/static'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
