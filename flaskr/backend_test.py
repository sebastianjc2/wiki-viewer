from flaskr.backend import Backend
from unittest.mock import MagicMock
import base64
import flask_testing

def mock_open(mock_value):
    class MockOpen:
        text = mock_value
        to_write = []

        def __init__(self, file_name, mode=''):
            pass

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            return self

        def read(self):
            return self.text

    return MockOpen


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
    

def test_get_wiki_page():
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_wiki_content_bucket = storage_client.bucket.return_value
    test_blob = test_wiki_content_bucket.get_blob.return_value 
    test_blob.open = mock_open("Test page :D")
    assert mocker.get_wiki_page('test.txt') == "Test page :D"


def test_upload_preexisting():
    storage_client = MagicMock()
    test_wiki_content_bucket = storage_client.bucket.return_value
    mocker = Backend(storage_client)
    test_blob = test_wiki_content_bucket.blob.return_value
    test_blob.exists.return_value = True
    file = MagicMock()
    file.filename.return_value("test.txt")

    assert mocker.upload(file) == "Exists"

def test_upload_pass():
    storage_client = MagicMock()
    test_wiki_content_bucket = storage_client.bucket.return_value
    mocker = Backend(storage_client)
    test_blob = test_wiki_content_bucket.blob.return_value
    file = MagicMock()
    file.filename.return_value("test.txt")
    test_blob.exists.return_value = False

    assert mocker.upload(file) == "Passed"

def test_sign_up_invalid():
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    assert mocker.sign_up('Invalid user\\ / ,', "testpass") == "Invalid characters in username."
    

def test_sign_up_taken_user():
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_blob = test_user_passwords.blob.return_value
    test_blob.exists.return_value = True
    assert mocker.sign_up('test', 'testpass') == 'Username is taken.'
    

def test_sign_up_success():
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_blob = test_user_passwords.blob.return_value
    test_blob.exists.return_value = False
    assert mocker.sign_up('blah', 'testpass') == 'Success'


def test_sign_in_username_fail():
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_blob = test_user_passwords.blob.return_value
    test_blob.exists.return_value = False
    assert mocker.sign_in('test', 'testpass') == 'Username Fail'

def test_sign_in_password_fail():
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_blob = test_user_passwords.blob.return_value
    test_blob.exists.return_value = True    
    test_blob.open = mock_open("d509c9802230283f6ec7b0ed811d15fa7271a97a37f9f0577c53e37bb68f7f5583858ab968648ec6c268213e7f92fff3db5293fc0e338c8e7973a8c95b9e10aa")
    assert mocker.sign_in('test', 'testpass123') == 'Password fail'

def test_sign_in_password_pass():
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_blob = test_user_passwords.blob.return_value
    test_blob.exists.return_value = True    
    test_blob.open = mock_open("d509c9802230283f6ec7b0ed811d15fa7271a97a37f9f0577c53e37bb68f7f5583858ab968648ec6c268213e7f92fff3db5293fc0e338c8e7973a8c95b9e10aa")
    assert mocker.sign_in('test', 'testpass') == 'Passed'

