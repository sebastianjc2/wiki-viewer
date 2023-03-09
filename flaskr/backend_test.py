from flaskr.backend import Backend
from unittest.mock import MagicMock
import base64


def test_get_all_page_names():
    storage_client = MagicMock()
    mocker = Backend(storage_client)

    storage_client.list_blobs.return_value = ["test.txt", "bla.txt"]

    assert mocker.get_all_page_names() == ["test.txt", "bla.txt"]

def test_get_image():
    storage_client = MagicMock()
    image_bucket = MagicMock()

    storage_client.bucket.return_value = image_bucket

    blob = MagicMock()
    image_bucket.get_blob.return_value = blob

    bytes_val = base64.b64encode(b"Test").decode("utf-8")
    blob.download_as_bytes.return_value = b"Test"

    blob.content_type = "image/jpeg"

    backend = Backend(storage_client)
    cont_type, img = backend.get_image("test.jpeg", "about")

    bytes_val = base64.b64encode(b"Test").decode("utf-8")
    
    assert img == bytes_val
    


