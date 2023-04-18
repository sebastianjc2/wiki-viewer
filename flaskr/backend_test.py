from flaskr.backend import Backend
from unittest.mock import MagicMock, patch
from flaskr.user import User
import base64


#Mock open function that is used in later methods that require reading a file
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

        def write(self, data):
            return data

    return MockOpen


''' Tests that get all page names is working by mocking the storage client and mocking the pages.
Once we call get all page names with the mocker, it should be the same list of pages as the return value we had set'''


def test_get_all_page_names():
    storage_client = MagicMock()
    mocker = Backend(storage_client)

    storage_client.list_blobs.return_value = ["test.txt", "bla.txt"]

    assert mocker.get_all_page_names() == ["test.txt", "bla.txt"]


''' Tests that the image is getting collected, downloaded as bytes, then encoded, decoded correctly '''


def test_get_image():
    storage_client = MagicMock()
    image_bucket = MagicMock()

    storage_client.bucket.return_value = image_bucket

    blob = MagicMock()
    image_bucket.get_blob.return_value = blob

    blob.download_as_bytes.return_value = b"Test"

    blob.content_type = "image/jpeg"

    backend = Backend(storage_client)
    cont_type, img = backend.get_image("test.jpeg", "about")

    bytes_val = base64.b64encode(b"Test").decode("utf-8")

    assert img == bytes_val


#Tests to see if the get wiki page method returns correctly
def test_get_wiki_page():
    #Mocking the storage, backend, bucket, and blob
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_wiki_content_bucket = storage_client.bucket.return_value
    test_blob = test_wiki_content_bucket.get_blob.return_value
    #Setting the open value using mock_open so that I can test without accessing
    #an actual file.
    test_blob.open = mock_open(
        '{"content" : ["Test page :D", "Test page line 2!"], "author" : "mock_user"}'
    )
    #Asserting that the return value is the same as the value I set for the mock open
    #Which lets me know it was opened correctly.
    assert mocker.get_wiki_page('test.txt') == [
        "Test page :D", "Test page line 2!"
    ]


#Tests the upload method in the case a file by the same name already exists
def test_upload_preexisting_fail():
    #Mocking the storage, backend, bucket, and blob
    storage_client = MagicMock()
    test_wiki_content_bucket = storage_client.bucket.return_value
    mocker = Backend(storage_client)
    test_blob = test_wiki_content_bucket.blob.return_value
    #Setting the return value for blob.exists to True since this is testing
    #if a file already exists by the same name
    test_blob.exists.return_value = True
    #Sets the mock value for what is returned when it is opened so that it can check the author
    test_blob.open = mock_open(
        '{"content" : ["Test page :D", "Test page line 2!"], "author" : "mock_user"}'
    )

    #Mocking the file class
    file = MagicMock()
    file.filename.return_value("test.txt")
    file.readlines.return_value = "Test page :D\nTest page line 2!"

    #Asserting that it returns 'Exists' which is what it should return if
    #it correctly found a prexisting file that was not authored by the current user.
    assert mocker.upload(file, "not_the_author") == "Exists"


#Tests the upload method in the case a file by the same name already exists
def test_upload_preexisting_pass():
    #Mocking the storage, backend, bucket, and blob
    storage_client = MagicMock()
    test_wiki_content_bucket = storage_client.bucket.return_value
    mocker = Backend(storage_client)
    test_blob = test_wiki_content_bucket.blob.return_value
    #Setting the return value for blob.exists to True since this is testing
    #if a file already exists by the same name
    test_blob.exists.return_value = True
    #Sets the mock value for what is returned when it is opened so that it can check the author
    test_blob.open = mock_open(
        '{"content" : ["Test page :D", "Test page line 2!"], "author" : "mock_user"}'
    )

    #Mocking the file class
    file = MagicMock()
    file.filename.return_value("test.txt")
    file.readlines.return_value = "Test page :D\nTest page line 2!"

    #Asserting that it returns passed which is what it should return if
    #it correctly recognized that the user matches the author of the prexisting file
    assert mocker.upload(file, "mock_user") == "Passed"


#Tests the upload method in the case it uploads without error
def test_upload_pass():
    #Mocking the storage, bucket
    storage_client = MagicMock()
    user_profile_bucket = MagicMock()

    #Mocking the file class
    file = MagicMock()
    file.filename.return_value("test.txt")

    storage_client.bucket.return_value = user_profile_bucket
    blob = MagicMock()
    user_profile_bucket.blob.return_value = blob

    # Setting a return value for blob.exists to false so it will run as if
    # there is no file by the same name, executing normally.
    blob.exists.return_value = False

    blob.open = mock_open("Test page :D")

    backend = Backend(storage_client)

    # Asserting that it returns 'Passed' which is what it should return if it doesn't
    # run into another file by the same name
    assert backend.upload(file, "test") == "Passed"


#Testing the signup function to make sure it will properly return when invalid
#characters are present in the user
def test_sign_up_invalid():
    #Mocks storage and backend
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    #Asserts that with this user containing all of the illegal characters, it will return
    #'Invalid characters in username.' which is what is expected when there are illegal characters
    assert mocker.sign_up("Bob", "Williams", 'Invalid user\\ / ,',
                          "testpass") == "Invalid characters in username."


#Testing the signup function to make sure it wont allow duplicate usernames/won't overwrite users
def test_sign_up_taken_user():
    #Mocking storage, backend, buckets, and blob
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_blob = test_user_passwords.blob.return_value
    #Setting the .exists return value to true to mock that username being taken
    test_blob.exists.return_value = True
    #Asserts 'Username is taken.', which is the expected return
    assert mocker.sign_up("Bob", "Williams", 'test',
                          'testpass') == 'Username is taken.'


#Testing a successful signup
def test_sign_up_success():
    #Mocking storage, backend, buckets, and blob
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_blob = test_user_passwords.blob.return_value
    #Setting the .exists return value to true to mock that username being free
    test_blob.exists.return_value = False
    #Asserts 'Success' for a successful signup
    assert mocker.sign_up("Bob", "Williams", 'blah', 'testpass') == 'Success'


def test_sign_up_two_different_buckets():
    #Mocking storage, backend, buckets, and blob
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_user_profile = storage_client.bucket.return_value
    test_blob_profile = test_user_profile.blob.return_value
    test_blob_pw = test_user_passwords.blob.return_value
    #Setting the .exists return value to true to mock that username being free
    test_blob_pw.exists.return_value = False
    #Asserts 'Success' for a successful signup
    assert mocker.sign_up("Bob", "Williams", 'blah', 'testpass') == 'Success'
    test_blob_profile.open.assert_called_with("w")
    test_blob_pw.open.assert_called_with("w")


#Testing a failed sign in for username
def test_sign_in_username_fail():
    #Mocking storage, backend, buckets, and blob
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_blob = test_user_passwords.blob.return_value
    #Setting the .exists return value to false to mock that username not exists
    test_blob.exists.return_value = False
    #Asserts that it returns "Username Fail" for a username not existing
    assert mocker.sign_in('test', 'testpass') == 'Username Fail'


#Testing a failed sign in for password
def test_sign_in_password_fail():
    #Mocking storage, backend, buckets, and blob
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_blob = test_user_passwords.blob.return_value
    #Setting the .exists return value to false to mock that username existing (so it doesnt fail for username)
    test_blob.exists.return_value = True
    #Setting up a mock open for the hashed password of test using testpass as the actual password
    test_blob.open = mock_open(
        "d509c9802230283f6ec7b0ed811d15fa7271a97a37f9f0577c53e37bb68f7f5583858ab968648ec6c268213e7f92fff3db5293fc0e338c8e7973a8c95b9e10aa"
    )
    #Asserts 'Password fail' for using the incorrect password here.
    assert mocker.sign_in('test', 'testpass123') == 'Password fail'


def test_sign_in_password_pass():
    #Mocking storage, backend, buckets, and blob
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_passwords = storage_client.bucket.return_value
    test_blob = test_user_passwords.blob.return_value
    #Setting the .exists return value to false to mock that username existing
    test_blob.exists.return_value = True
    #Setting up a mock open for the hashed password of test using testpass as the actual password
    test_blob.open = mock_open(
        "d509c9802230283f6ec7b0ed811d15fa7271a97a37f9f0577c53e37bb68f7f5583858ab968648ec6c268213e7f92fff3db5293fc0e338c8e7973a8c95b9e10aa"
    )
    #Asserts 'Passed' for successfully signing in using the correct password
    assert mocker.sign_in('test', 'testpass') == 'Passed'


'''
def test_get_favorites_list():
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user = User("test")
    test_user_info = storage_client.bucket.return_value
    test_blob = test_user_info.blob.return_value

    test_blob.open = mock_open('test1,test2')
    test_blob.download_as_string.return_value.decode.return_value = 'test1,test2'
    assert mocker.get_favorites_list(test_user) == ['test1', 'test2']
'''


def test_get_user_info():
    '''Tests the get_user_info function by making sure that it returns the expected info
    which means it correctly collected the user's information. '''
    # Mocking the storage client, the backend, the bucket and the blobs.
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_info = storage_client.bucket.return_value
    test_blob = test_user_info.blob.return_value

    # using mock open to mock the user.open("r") as f command
    test_blob.open = mock_open('{"test1":"test", "test2":"test"}')

    assert mocker.get_user_info("test") == {"test1": "test", "test2": "test"}


def test_helper_update_user_info():
    ''' Tests the update_user_info function. '''
    # Mocking the storage client, the backend, the bucket and the blobs.
    storage_client = MagicMock()
    backend = Backend(storage_client)
    with patch("flaskr.backend.Backend.get_user_info",
               return_value={
                   "first_name": "Sebastian",
                   "last_name": "Test",
                   "username": "sebastiantest",
                   "pages_authored": [],
                   "bio": "test",
                   "DOB": "test",
                   "location": "test"
               }):
        assert str(
            backend.helper_update_user_info("sebastiantest", "random bio",
                                            "2022-01-01", "USA")
        ) == '{"first_name": "Sebastian", "last_name": "Test", "username": "sebastiantest", "pages_authored": [], "bio": "random bio", "DOB": "2022-01-01", "location": "USA"}'


def test_get_favorites_list():
    storage_client = MagicMock()
    mocker = Backend(storage_client)
    test_user_info = storage_client.bucket.return_value
    test_blob = test_user_info.blob.return_value

    # using mock open to mock the user.open("r") as f command
    test_blob.open = mock_open(
        '{"test1":"test", "test2":"test", "favorites":["favorite1"]}')
    user = User("usertest")
    assert mocker.get_favorites_list(user) == ["favorite1"]


def test_helper_update_favorites_list_add():
    storage_client = MagicMock()
    backend = Backend(storage_client)
    user = User("usertest")
    with patch("flaskr.backend.Backend.get_user_info",
               return_value={
                   "first_name": "userfirst",
                   "last_name": "userlast",
                   "username": "usertest",
                   "pages_authored": [],
                   "favorites": [],
                   "bio": "test",
                   "DOB": "test",
                   "location": "test"
               }):
        assert str(
            backend.helper_update_favorites_list(user, "pagetest", "add")
        ) == '{"first_name": "userfirst", "last_name": "userlast", "username": "usertest", "pages_authored": [], "favorites": ["pagetest"], "bio": "test", "DOB": "test", "location": "test"}'


def test_helper_update_favorites_list_remove():
    storage_client = MagicMock()
    backend = Backend(storage_client)
    user = User("usertest")
    with patch("flaskr.backend.Backend.get_user_info",
               return_value={
                   "first_name": "userfirst",
                   "last_name": "userlast",
                   "username": "usertest",
                   "pages_authored": [],
                   "favorites": ["favorite1"],
                   "bio": "test",
                   "DOB": "test",
                   "location": "test"
               }):
        assert str(
            backend.helper_update_favorites_list(user, "favorite1", "remove")
        ) == '{"first_name": "userfirst", "last_name": "userlast", "username": "usertest", "pages_authored": [], "favorites": [], "bio": "test", "DOB": "test", "location": "test"}'
