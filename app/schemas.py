from pydantic import BaseModel, ConfigDict


class CreateMatchSchema(BaseModel):
    player1_name: str
    player2_name: str

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, str_max_length=255
    )
