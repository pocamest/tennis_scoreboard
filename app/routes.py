from app.controllers import PlayerController
from app.router import Router


def register_routes(router: Router, player_controller: PlayerController) -> None:
    router.add_route(method='GET', path='/', handler=player_controller.hello)
