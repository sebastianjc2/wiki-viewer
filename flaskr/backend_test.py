from flaskr.backend import Backend
from unittest.mock import MagicMock


def test_get_all_page_names():
    storage_client = MagicMock()
    mocker = Backend(storage_client)

    storage_client.list_blobs.return_value = ["test.txt", "bla.txt"]

    assert mocker.get_all_page_names() == ["test.txt", "bla.txt"]