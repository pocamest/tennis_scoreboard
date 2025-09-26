from app.controllers import MainController, MatchController
from app.router import Router


def register_routes(
    router: Router, main_ctrl: MainController, match_ctrl: MatchController
) -> None:
    router.add_route(method='GET', path='/', handler=main_ctrl.show_index_page)
    router.add_route(
        method='GET', path='/new-match', handler=match_ctrl.show_new_match_page
    )
    router.add_route(
        method='POST',
        path='/new-match',
        handler=match_ctrl.handle_new_match_creation,
    )
    router.add_route(
        method='GET', path='/match-score', handler=match_ctrl.show_match_score_page
    )
    router.add_route(
        method='POST', path='/match-score', handler=match_ctrl.handle_score_update
    )
