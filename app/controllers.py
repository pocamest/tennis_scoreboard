from jinja2 import Environment


class MainController:
    def __init__(self, jinja_env: Environment):
        self._jinja = jinja_env

    def show_index_page(self) -> tuple[str, list[tuple[str, str]], str]:
        template = self._jinja.get_template('index.html')
        html_body = template.render()

        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        return status, headers, html_body
