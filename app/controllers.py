from typing import Any

from jinja2 import Environment
from pydantic import ValidationError

from app.schemas import CreateMatchSchema
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
