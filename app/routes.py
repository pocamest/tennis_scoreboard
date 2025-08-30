from app.controllers import MainController, MatchController
from app.router import Router


def register_routes(
    router: Router, main_controller: MainController, match_controller: MatchController
) -> None:
    router.add_route(method='GET', path='/', handler=main_controller.show_index_page)
    router.add_route(
        method='GET', path='/new-match', handler=match_controller.show_new_match_page
    )
    router.add_route(
        method='POST',
        path='/new-match',
        handler=match_controller.handle_new_match_creation,
    )
