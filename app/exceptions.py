class AppError(Exception):
    pass

class MatchNotFoundError(AppError):
    pass

class InconsistentMatchStateError(AppError):
    pass
