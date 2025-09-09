import uuid as uuid_pkg

from app.domain import OngoingMatch


class OngoingMatchStore:
    def __init__(self) -> None:
        self._matches: dict[uuid_pkg.UUID, OngoingMatch] = {}

    def put(self, match_obj: OngoingMatch) -> None:
        self._matches[match_obj.uuid] = match_obj

    def delete(self, uuid: uuid_pkg.UUID) -> None:
        self._matches.pop(uuid, None)

    def find_one(self, uuid: uuid_pkg.UUID) -> OngoingMatch | None:
        return self._matches.get(uuid)
