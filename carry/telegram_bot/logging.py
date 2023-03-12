import logging
from typing import TypeVar, Callable, Awaitable, ParamSpec
from functools import wraps

P = ParamSpec("P")
RT = TypeVar("RT")
Func = Callable[P, Awaitable[RT]]
log = logging.getLogger(__name__)


def log_handler(func: Func) -> Func:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Awaitable[RT]:
        func_name = func.__name__
        try:
            result = await func(*args, **kwargs)
            log.info(f"[CARRY] Handler '{func_name}' processed message")
            return result
        except Exception:
            log.exception(
                f"[CARRY] Get exception during '{func_name}' handler work"
            )
            raise

    return wrapper
