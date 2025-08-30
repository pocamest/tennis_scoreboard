from collections.abc import Iterable
from urllib.parse import parse_qs
from wsgiref.types import StartResponse, WSGIEnvironment

from jinja2 import Environment, FileSystemLoader
from waitress import serve
from whitenoise import WhiteNoise

from app import (
    Database,
    MainController,
    MatchController,
    MatchService,
    OngoingMatchStore,
    Router,
    register_routes,
)
from app.settings import settings


class App:
    def __init__(self, router: Router):
        self._router = router

    def __call__(
        self, environ: WSGIEnvironment, start_response: StartResponse
    ) -> Iterable[bytes]:
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']

        handler, path_params = self._router.resolve(method=method, path=path)
        if handler is None or path_params is None:
            status = '404 Not Found'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            start_response(status, headers)
            return [b'<h1>404 Not Found</h1>']

        parsed_query_params = parse_qs(environ.get('QUERY_STRING', ''))
        query_params = self._unpack_data(parsed_query_params)
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        request_body = environ['wsgi.input'].read(request_body_size)
        parsed_form_data = parse_qs(request_body.decode('utf-8'))
        form_data = self._unpack_data(parsed_form_data)

        kwargs = {**path_params, **query_params, **form_data}

        try:
            status, headers, body = handler(**kwargs)
            start_response(status, headers)
            return [body.encode('utf-8')]

        except Exception:
            status = '500 Internal Server Error'
            headers = [('Content-type', 'text/html; charset=utf-8')]
            start_response(status, headers)
            return [b'<h1>500 Internal Server Error</h1>']

    def _unpack_data(self, raw_data: dict[str, list[str]]) -> dict[str, str]:
        data = {}
        for key, value in raw_data.items():
            if len(value) > 1:
                raise ValueError(
                    f"Получено несколько значений для '{key}', но ожидалось одно."
                )
            data[key] = value[0]
        return data


router = Router()
jinja_env = Environment(loader=FileSystemLoader(settings.template_dir))
ongoing_match_store = OngoingMatchStore()
db = Database(db_url=settings.db_url, echo=settings.db_echo)
match_srv = MatchService(db=db, ongoing_match_store=ongoing_match_store)
main_ctrl = MainController(jinja_env=jinja_env)
match_ctrl = MatchController(jinja_env=jinja_env, match_srv=match_srv)
register_routes(
    router=router, main_ctrl=main_ctrl, match_ctrl=match_ctrl
)
application = App(router=router)
application_with_static = WhiteNoise(
    application=application, root=settings.static_dir, prefix=settings.static_url
)


if __name__ == '__main__':
    serve(application_with_static, host=settings.app_host, port=settings.app_port)
