from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Player


class PlayerRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_one_by_name(self, name: str) -> Player | None:
        stmt = select(Player).where(Player.name == name)
        return self._session.scalars(stmt).one_or_none()

    def add(self, player: Player) -> None:
        self._session.add(player)

    def find_or_create(self, name: str) -> Player:
        player = self.find_one_by_name(name)
        if player is None:
            player = Player(name=name)
            self._session.add(player)
        return player
