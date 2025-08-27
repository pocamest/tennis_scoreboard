from app.controllers import MainController
from app.router import Router


def register_routes(router: Router, main_controller: MainController) -> None:
    router.add_route(method='GET', path='/', handler=main_controller.show_index_page)
