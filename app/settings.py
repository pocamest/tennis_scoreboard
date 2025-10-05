from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    db_url: str
    db_echo: bool = False

    app_host: str = '127.0.0.1'
    app_port: int = 8080

    base_dir: Path = BASE_DIR
    template_dir: Path = base_dir / 'app' / 'templates'
    static_dir: Path = base_dir / 'app' / 'static'

    static_url: str = '/static'

    default_page_size: int = 5

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
