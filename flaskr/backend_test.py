from flaskr.backend import Backend
from unittest.mock import MagicMock


def test_get_all_page_names():
    storage_client = MagicMock()
    mocker = Backend(storage_client)

    storage_client.list_blobs.return_value = ["test.txt", "bla.txt"]

    assert mocker.get_all_page_names() == ["test.txt", "bla.txt"]

def test_get_image():
    storage_client = MagicMock()
    image_bucket = MagicMock()
    backend = Backend(storage_client)

    storage_client.bucket.return_value = image_bucket

    blob = MagicMock()
    image_bucket.get_blob.return_value = blob

    blob.download_as_bytes.return_value = b"Test"

    blob.content_type.return_value = "image/jpeg"

    test = backend.get_image("test.jpeg", "about")
    print(test)


