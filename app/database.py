from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class Database:
    def __init__(self, db_url: str, echo: bool):
        self._engine = create_engine(url=db_url, echo=echo)
        self._session_factory = sessionmaker(bind=self._engine, autoflush=False)

    @contextmanager
    def get_session(self) -> Generator[Session]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
