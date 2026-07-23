import sys
from pathlib import Path

import httpx2
import pytest

import httpx_aiohttp
from httpx_aiohttp import Httpx2AiohttpClient
from httpx_aiohttp.httpx2 import AiohttpTransport

PACKAGE_DIR = Path(__file__).resolve().parents[2] / "src" / "httpx_aiohttp"

HTTPX2_IMPORT_LINE = "import httpx2 as httpx"


@pytest.mark.parametrize("module", ["transport.py", "client.py"])
def test_httpx2_modules_stay_in_sync(module: str) -> None:
    """The httpx2 variant modules must be identical to the httpx ones,
    except for the httpx2 import and the client class name."""
    original = (PACKAGE_DIR / module).read_text()
    variant = (PACKAGE_DIR / "httpx2" / module).read_text()

    normalized = variant.replace(HTTPX2_IMPORT_LINE, "import httpx").replace(
        "Httpx2AiohttpClient", "HttpxAiohttpClient"
    )
    assert normalized == original


def test_top_level_lazy_export() -> None:
    assert issubclass(Httpx2AiohttpClient, httpx2.AsyncClient)


def test_star_import() -> None:
    namespace: dict = {}
    exec("from httpx_aiohttp import *", namespace)
    assert "HttpxAiohttpClient" in namespace
    assert "AiohttpTransport" in namespace
    assert "Httpx2AiohttpClient" in namespace


def test_unknown_attribute_raises() -> None:
    with pytest.raises(AttributeError):
        httpx_aiohttp.does_not_exist


class BlockHttpx2Import:
    def find_spec(self, name, path=None, target=None):
        if name == "httpx2" or name.startswith("httpx2."):
            raise ModuleNotFoundError(f"No module named {name!r}")
        return None


def test_helpful_error_when_httpx2_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Users who install httpx-aiohttp without the `httpx2` extra should get
    an ImportError pointing at it."""
    for module in list(sys.modules):
        if module == "httpx2" or module.startswith(("httpx2.", "httpx_aiohttp.httpx2")):
            monkeypatch.delitem(sys.modules, module)
    monkeypatch.setattr(sys, "meta_path", [BlockHttpx2Import()] + sys.meta_path)

    with pytest.raises(ImportError, match=r"httpx-aiohttp\[httpx2\]"):
        httpx_aiohttp.Httpx2AiohttpClient


def test_httpx2_client_uses_aiohttp_transport() -> None:
    client = Httpx2AiohttpClient()
    assert isinstance(client._transport, AiohttpTransport)


def test_httpx2_client_respects_explicit_transport() -> None:
    transport = AiohttpTransport()
    client = Httpx2AiohttpClient(transport=transport)
    assert client._transport is transport
