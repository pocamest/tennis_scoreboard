from pydantic import BaseModel, ConfigDict, field_validator

from app.domain import PlayerIdentifier


class CreateMatchSchema(BaseModel):
    player1_name: str
    player2_name: str

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, str_max_length=255
    )


class PointWinnerSchema(BaseModel):
    point_winner: PlayerIdentifier

    @field_validator('point_winner', mode='before')
    @classmethod
    def to_enum(cls, value: str) -> PlayerIdentifier:
        try:
            return PlayerIdentifier(int(value))
        except (ValueError, TypeError):
            raise ValueError('point_winner must be "0" or "1"')
