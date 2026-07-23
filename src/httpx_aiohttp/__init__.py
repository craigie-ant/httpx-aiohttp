import typing as t
from importlib.util import find_spec

from .client import HttpxAiohttpClient
from .transport import AiohttpTransport

if t.TYPE_CHECKING:
    from .httpx2 import Httpx2AiohttpClient as Httpx2AiohttpClient

__all__ = ["AiohttpTransport", "HttpxAiohttpClient"]

if find_spec("httpx2") is not None:
    __all__ += ["Httpx2AiohttpClient"]


def __getattr__(name: str) -> t.Any:
    if name == "Httpx2AiohttpClient":
        try:
            from .httpx2 import Httpx2AiohttpClient
        except ModuleNotFoundError as exc:
            raise ImportError(
                "Httpx2AiohttpClient requires the `httpx2` package, which is not installed. "
                "Install it with `pip install httpx-aiohttp[httpx2]`."
            ) from exc
        return Httpx2AiohttpClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
