import uuid as uuid_pkg
from typing import Any

from jinja2 import Environment
from pydantic import ValidationError

from app.exceptions import MatchNotFoundError
from app.schemas import CreateMatchSchema, PointWinnerSchema
from app.services import MatchService


class MainController:
    def __init__(self, jinja_env: Environment):
        self._jinja = jinja_env

    def show_index_page(self) -> tuple[str, list[tuple[str, str]], str]:
        template = self._jinja.get_template('index.html')
        html_body = template.render()

        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        return status, headers, html_body


class MatchController:
    def __init__(self, jinja_env: Environment, match_srv: MatchService):
        self._jinja = jinja_env
        self._match_srv = match_srv

    def show_new_match_page(self) -> tuple[str, list[tuple[str, str]], str]:
        template = self._jinja.get_template('new-match.html')
        html_body = template.render()

        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        return status, headers, html_body

    def handle_new_match_creation(
        self, **form_data: Any
    ) -> tuple[str, list[tuple[str, str]], str]:
        try:
            validated_data = CreateMatchSchema(**form_data)
        except ValidationError:
            template = self._jinja.get_template('new-match.html')

            context = {
                'error_message': 'Ошибка: Имена игроков не корректны.',
                'player1_name': form_data.get('player1_name'),
                'player2_name': form_data.get('player2_name'),
            }

            html_body = template.render(context)

            status = '400 Bad Request'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            return status, headers, html_body

        ongoing_match = self._match_srv.create_new_match(
            player1_name=validated_data.player1_name,
            player2_name=validated_data.player2_name,
        )

        status = '303 See Other'
        headers = [('Location', f'/match-score?uuid={ongoing_match.uuid}')]
        body = ''
        return status, headers, body

    def show_match_score_page(
        self, uuid: str
    ) -> tuple[str, list[tuple[str, str]], str]:
        try:
            match_uuid = uuid_pkg.UUID(uuid)

            ongoing_match = self._match_srv.get_ongoing_match(match_uuid)
        except ValueError:
            status = '400 Bad Request'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            html_body = '<h1>400 Bad Request: Invalid UUID format</h1>'
            return status, headers, html_body
        except MatchNotFoundError:
            status = '404 Not Found'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            html_body = '<h1>404 Not Found: Match not found</h1>'
            return status, headers, html_body

        context = ongoing_match.get_view_model()

        template = self._jinja.get_template('match-score.html')
        html_body = template.render(context)

        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        return status, headers, html_body

    def handle_score_update(
        self, uuid: str, **form_data: Any
    ) -> tuple[str, list[tuple[str, str]], str]:
        try:
            match_uuid = uuid_pkg.UUID(uuid)
            validated_data = PointWinnerSchema(**form_data)
            ongoing_match = self._match_srv.record_point(
                uuid=match_uuid, point_winner=validated_data.point_winner
            )
        except ValueError:
            status = '400 Bad Request'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            html_body = '<h1>400 Bad Request: Invalid UUID format</h1>'
            return status, headers, html_body
        except MatchNotFoundError:
            status = '404 Not Found'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            html_body = '<h1>404 Not Found: Match not found</h1>'
            return status, headers, html_body

        context = ongoing_match.get_view_model()

        template = self._jinja.get_template('match-score.html')
        html_body = template.render(context)

        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        return status, headers, html_body

    def show_matches_page(
        self, page: str = '1', filter_by_player_name: str | None = None
    ) -> tuple[str, list[tuple[str, str]], str]:
        try:
            page_num = int(page)
            if page_num < 1:
                page_num = 1
        except (ValueError, TypeError):
            page_num = 1

        paginated_data = self._match_srv.get_finished_matches_paginated(
            page=page_num, player_name=filter_by_player_name
        )

        context = {**paginated_data, 'filter_by_player_name': filter_by_player_name}

        template = self._jinja.get_template('matches.html')
        html_body = template.render(context)

        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        return status, headers, html_body
