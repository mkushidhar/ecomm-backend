from ecomm.main import root


def test_root_returns_status_working() -> None:
    assert root() == {"status": "working"}
