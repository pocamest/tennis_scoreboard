class PlayerController:
    def __init__(self) -> None:
        pass

    def hello(self) -> tuple[str, list[tuple[str, str]], str]:
        return (
            '200 OK',
            [('Content-type', 'text/html; charset=utf-8')],
            '<h1>Hello, World!</h1>'
        )
