from flaskr import create_app
from flask import render_template, request, url_for
from flaskr import pages
from flaskr import Backend
from flask_wtf import csrf
from flaskr.user import User
from unittest.mock import MagicMock, patch
from flask_login import current_user, FlaskLoginClient, login_user, logout_user, LoginManager
from flaskr.pages import LoginForm, SignupForm
import pytest
import io
import unittest

# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing
''' FIXTURES FOR LOGGED OUT FEATURES '''


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


''' Tests the home page while logged out, it asserts that Welcome to the Wiki! is in the resp.data when you get "/", because Welcome to the Wiki, {{user}}
would show up if a user is logged in.'''


def test_home_page_while_logged_out(app, client):
    resp = client.get("/")
    #print(resp.data)
    assert resp.status_code == 200
    with app.app_context():
        expected = render_template("home.html", user=current_user)
        #print(expected)
        assert b"Welcome to the Wiki!" in resp.data
        assert expected == resp.data.decode("utf-8")


'''It tests that the about page status_code after doing client.get is correct, which means it did GET correctly, and also asserts that our names are in
the template, as well as in the resp.text'''


def test_about(app, client):
    with app.app_context():
        with patch("flaskr.backend.Backend.get_image",
                   return_value=("test1", "test2")):
            resp = client.get("/about")
            assert resp.status_code == 200
            expected = render_template("about.html", user=current_user)
            assert "Sebastian Caballero" in resp.text and "Sebastian Caballero" in expected
            assert "Christopher Cordero" in resp.text and "Christopher Cordero" in expected
            assert "Chelsea Garcia" in resp.text and "Chelsea Garcia" in expected


''' Test for the /pages route. We first mock 2 file names, and add them into the list. We mock get_all_page_names from the backend to return said list.
Then, we verify that when going into the /pages route, the status code is 200, and the filenames that we added should be in resp.data.'''


def test_pages_not_logged_in(app, client):
    file1 = MagicMock()
    file1.name = "test.txt"

    file2 = MagicMock()
    file2.name = "blah.txt"
    with patch("flaskr.backend.Backend.get_all_page_names",
               return_value=[file1, file2]):
        resp = client.get("/pages")
        #print(resp.data)
        assert resp.status_code == 200
        assert b"Pages contained in this Wiki" in resp.data
        assert b"bla" in resp.data
        assert b"test" in resp.data


'''Test for the individual page routing (/pages/<page>). We give it a string containing what should be in the page, and then mock the "get_wiki_page"
backend method to return that string. Then once we do client.get(/pages/Ataxia), we assert that the string is inside that response.'''


def test_individual_page(app, client):
    file1 = [
        "Ataxia was a short-lived American experimental rock supergroup formed in 2004 by guitarist John Frusciante (Red Hot Chili Peppers), bassist Joe Lally (Fugazi) and drummer Josh Klinghoffer (Dot Hacker, The Bicycle Thief), who later succeeded Frusciante as the lead guitarist of the Red Hot Chili Peppers until 2019, at which point Frusciante rejoined the band. Ataxia wrote and recorded songs for two weeks, and the material was separated into two albums: Automatic Writing (2004) and AW II (2007). The songs all feature a ground-bass line with the guitar overlaying different motifs and long developments."
    ]
    with patch("flaskr.backend.Backend.get_wiki_page", return_value=file1):
        resp = client.get("/pages/Ataxia")
        assert resp.status_code == 200
        print(resp.data.decode("utf-8"))
        assert file1[0] in resp.data.decode("utf-8")


''' Same as above, with also a test page name'''


def test_individual_page_routing(app, client):
    file1 = ["This is a test file"]
    page_name = "test"

    with patch("flaskr.backend.Backend.get_wiki_page", return_value=file1):
        resp = client.get("/pages/<page_name>")
        assert resp.status_code == 200
        print(resp.data.decode("utf-8"))
        assert file1[0] in resp.data.decode("utf-8")


''' NEW FIXTURES FOR LOGIN RELATED TESTS'''


@pytest.fixture
def app2():
    app2 = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })
    return app2


@pytest.fixture
def client2(app2):
    app2.test_client_class = FlaskLoginClient
    return app2.test_client(app2.test_client_class)


''' This tests the navbar (and at the same time, the home page) changes once a user is logged in.
We do that by creating a user and passing it to the test client, and by creating the user, .is_authenticated is turned on by default.
So, once the response gets the / route, it will see the changes in the navbar, and also the username in both the navbar and the home page.'''


def test_navbar_and_home_page_change_when_logged_in(app2, client2):
    user = User("Sebastian")
    with app2.test_client(user=user) as c:
        resp = c.get("/")
        assert resp.status_code == 200
        expected = render_template("home.html", user=user)
        assert "Sebastian" in expected
        assert "Welcome to the Wiki, Sebastian!" in expected
        assert "Logout" in expected
        assert expected == resp.text


def test_user_GET(app2, client2):
    user = User("Sebastian")
    with app2.test_client(user=user) as c:
        with patch("flaskr.backend.Backend.get_user_info",
                   return_value={
                       "username": "swiki",
                       "first_name": "Sebastian",
                       "last_name": "Test",
                       "pages_authored": ["test1.txt", "test2.txt"],
                   }):
            resp = c.get("/user")
            print(resp.text)
            assert resp.status_code == 200
            assert "Sebastian" in resp.text
            assert "swiki" in resp.text
            assert "Test" in resp.text
            assert "Pages authored" in resp.text
            assert "test1.txt" in resp.text and "test2.txt" in resp.text


''' It tests that the response is correctly GETting the login template (when the /login route is called)'''


def test_login_template(app2, client2):
    with app2.app_context():
        form = MagicMock()
        resp = client2.get("/login")
        assert resp.status_code == 200
        #print(resp.text)
        expected = render_template("login.html", form=form, user=current_user)
        #print(expected)
        assert "username" in expected and "username" in resp.text
        assert "password" in expected and "password" in resp.text
        assert "submit" in expected and "submit" in resp.text
        assert "Login" in expected and "Login" in resp.text


''' It tests the POST method of the /login route (when the form is submitted). For this, we mock the sign_in backend method to return "Passed"
which means that everything went well (it was a valid and existing username and password). Then, we give it some dummy data to enter in the fields
with the username "Bob". Since we have redirects to be automatically followed, we assert that "Bob" is in resp.text, which should be the home page
template, because Bob will appear in both the "Welcome to the Wiki, Bob!" message, and in the navbar.'''


def test_login_post_redirects_TRUE(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in", return_value="Passed"):
            resp = c.post("/login",
                          data={
                              "csrf_token": "Ignore",
                              "username": "Bob",
                              "password": "test1234",
                              "submit": "Login"
                          },
                          follow_redirects=True)
            assert "Bob" in resp.text
            assert resp.status_code == 200  # Means it already redirected to home
            # Already redirected because follow_redirects=True


''' It tests the POST method of the /login route (when the form is submitted). For this, we mock the sign_in backend method to return "Passed"
which means that everything went well (it was a valid and existing username and password). Then, we give it some dummy data to enter in the fields
with the username "Bob". Since we have redirects to NOT be automatically followed, we assert that "Redirecting" is in resp.text, which is what it says
if the redirect is taking too long. We also test the status code to be 302, which indicates temporary redirecting.'''


def test_login_post_auto_redirects_FALSE(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in", return_value="Passed"):
            resp = c.post("/login",
                          data={
                              "csrf_token": "Ignore",
                              "username": "Bob",
                              "password": "test1234",
                              "submit": "Login"
                          },
                          follow_redirects=False)

            assert "Redirecting" in resp.text
            assert resp.status_code == 302  # Mean's its in the process of redirecting
            # Hasn't redirected yet because follow_redirects=False


''' It tests the POST method of the /login route (when the form is submitted). For this, we mock the sign_in backend method to return "Password Fail"
which means that the user entered a wrong password (that doesn't match the username). Then, we assert that it takes you to the page where it says "Password
is incorrect."'''


def test_login_post_wrong_password(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in",
                   return_value="Password fail"):
            resp = c.post("/login",
                          data={
                              "csrf_token": "Ignore",
                              "username": "Bob",
                              "password": "test1234",
                              "submit": "Login"
                          })
            assert resp.text == "Password is incorrect."


''' It tests the POST method of the /login route (when the form is submitted). For this, we mock the sign_in backend method to return "Username Fail"
which means that the user entered a non existing username. Then, we assert that it takes you to the page where it says "That username does not exist."'''


def test_login_post_non_existing_username(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in",
                   return_value="Username Fail"):
            resp = c.post("/login",
                          data={
                              "csrf_token": "Ignore",
                              "username": "Bob",
                              "password": "test1234",
                              "submit": "Login"
                          })
            assert resp.text == "That username does not exist."


''' It tests that the response is correctly GETting the signup template (when the /signup route is called)'''


def test_signup_template(app2, client2):
    with app2.app_context():
        form = MagicMock()
        # form.username = '<input id="username" maxlength="25" minlength="3" name="username" required type="text" value="Bob">'
        # form.hidden_tag.return_value = '<input id="csrf_token" name="csrf_token" type="hidden" value="IjhmYzQzOGY4MDQyYmI5YmM4OWU5MTQ5YjFlMTYxOTQ3NzQ3MjYwODAi.ZAea6Q.chsyN2xGVvv9Q7RWn8RnVvcRqEs">'
        resp = client2.get("/signup")
        assert resp.status_code == 200
        #print(resp.text)
        expected = render_template("signup.html", form=form, user=current_user)
        #print(expected)
        assert "username" in expected and "username" in resp.text
        assert "password" in expected and "password" in resp.text
        assert "submit" in expected and "submit" in resp.text
        assert "Sign Up" in expected and "Sign Up" in resp.text


''' It tests the POST method of the /signup route (when the form is submitted). For this, we mock the sign_up backend method to return "Success"
which means that everything went well (it was a valid and unique username). Then, we give it some dummy data to enter in the fields
with the username "Bob". Since we have redirects to be automatically followed, we assert that "Bob" is in resp.text, which should be the home page
template, because Bob will appear in both the "Welcome to the Wiki, Bob!" message, and in the navbar.'''


def test_signup_post_redirects_TRUE(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_up", return_value="Success"):
            resp = c.post("/signup",
                          data={
                              "csrf_token": "Ignore",
                              "first_name": "Bob",
                              "last_name": "Williams",
                              "username": "Bob",
                              "password": "test1234",
                              "submit": "Login"
                          },
                          follow_redirects=True)
            assert "Bob" in resp.text
            assert resp.status_code == 200  # Means it already redirected to home
            # Already redirected because follow_redirects=True


''' It tests the POST method of the /signup route (when the form is submitted). For this, we mock the sign_up backend method to return "Success"
which means that everything went well (it was a valid and unique username). Then, we give it some dummy data to enter in the fields
with the username "Bob". Since we have redirects to NOT be automatically followed, we assert that "Redirecting" is in resp.text, which is what it says
if the redirect is taking too long. We also test the status code to be 302, which indicates temporary redirecting.'''


def test_signup_post_auto_redirects_FALSE(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_up", return_value="Success"):
            resp = c.post("/signup",
                          data={
                              "csrf_token": "Ignore",
                              "first_name": "Bob",
                              "last_name": "Williams",
                              "username": "Bob",
                              "password": "test1234",
                              "submit": "Login"
                          },
                          follow_redirects=False)

            assert "Redirecting" in resp.text
            assert resp.status_code == 302  # Mean's its in the process of redirecting
            # Hasn't redirected yet because follow_redirects=False


''' It tests the POST method of the /signup route (when the form is submitted). For this, we mock the sign_up backend method to return "Username is taken."
which means that the user entered a username that already exists in the database. Then, we assert that it takes you to the page where it says "That username
is already taken."'''


def test_signup_post_username_already_taken(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_up",
                   return_value="Username is taken."):
            resp = c.post("/signup",
                          data={
                              "csrf_token": "Ignore",
                              "first_name": "Bob",
                              "last_name": "Williams",
                              "username": "Bob",
                              "password": "test1234",
                              "submit": "Login"
                          })
            assert resp.text == "That username is already taken."


def test_signup_post_invalid_characters(app2, client2):
    ''' It tests the POST method of the /signup route (when the form is submitted). For this, we mock the sign_up backend method to return "Invalid characters in username."
    which means that the user entered a username that has invalid characters (" ", "/", ",", etc"). Then, we assert that it takes you to the page where it says 
    "Invalid characters in username."'''
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_up",
                   return_value="Invalid characters in username."):
            resp = c.post("/signup",
                          data={
                              "csrf_token": "Ignore",
                              "first_name": "Bob",
                              "last_name": "Williams",
                              "username": "Bob",
                              "password": "test1234",
                              "submit": "Login"
                          })
            assert resp.text == "Invalid characters in username."


'''Tests the GET method of the /logout route, which should be the logout.html template. Checks that the status code is 302, because it should redirect you to home page after logging out'''


def test_log_out(app2, client2):
    user = User("Sebastian")
    assert user.is_anonymous == False
    with app2.test_client(user=user) as c:
        resp = c.get("/logout")
        assert resp.status_code == 302  # should be 302 because we should be redirecting to home page
        assert current_user.is_anonymous == True  # should be True now, since we are being logged out


''' Tests the POST method of the /logout route. Asserts that the user is now anonymous since we're being logged out, that we got redirected, since follow_redirects = True,
and that Welcome to the Wiki! is now in the response text, because by that point we should be in the home page'''


def test_log_out_redirects_TRUE(app2, client2):
    user = User("Sebastian")
    assert user.is_anonymous == False
    with app2.test_client(user=user) as c:
        resp = c.post("/logout", follow_redirects=True)
        assert resp.status_code == 200  # should be 200 because redirects are on, so we should be at the home page now
        assert current_user.is_anonymous == True  # should be True now, since we are being logged out
        assert "Welcome to the Wiki!" in resp.text  # should be True because we should have been redirected to the home page


def test_pages_logged_in_GET(app2, client2):
    user = User("Chelsea")
    file1 = MagicMock()
    file1.name = "test.txt"

    file2 = MagicMock()
    file2.name = "blah.txt"

    with app2.test_client(user=user) as c:
        with patch("flaskr.backend.Backend.get_all_page_names",
                   return_value=[file1, file2]):
            with patch("flaskr.backend.Backend.get_favorites_list",
                       return_value=[file1]):
                resp = c.get("/pages")
                print(resp.data)
                assert resp.status_code == 200

                assert b"Favorites List" in resp.data
                assert b"Pages contained in this Wiki" in resp.data
                assert b"blah" in resp.data
                assert b"test" in resp.data


def test_pages_logged_in_POST_TRUE(app2, client2):
    user = User("Chelsea")
    file1 = MagicMock()
    file1.name = "test.txt"

    file2 = MagicMock()
    file2.name = "blah.txt"

    with app2.test_client(user=user) as c:
        with patch("flaskr.backend.Backend.get_all_page_names",
                   return_value=[file1, file2]):
            with patch("flaskr.backend.Backend.get_favorites_list",
                       return_value=["test1", "test2"]):
                with patch("flaskr.backend.Backend.add_favorite"):
                    resp = c.post("/pages",
                                  data={
                                      "page_name": "test",
                                      "edit_type": "add"
                                  },
                                  follow_redirects=True)
                    assert resp.status_code == 200

                    assert b"Favorites List" in resp.data
                    assert b"Pages contained in this Wiki" in resp.data
                    assert b"blah" in resp.data
                    assert b"test" in resp.data


def test_user_GET(app2, client2):
    user = User("Sebastian")
    with app2.test_client(user=user) as c:
        with patch("flaskr.backend.Backend.get_user_info",
                   return_value={
                       "username": "sebastiantest",
                       "first_name": "Sebastian",
                       "last_name": "Test",
                       "pages_authored": ["test1.txt", "test2.txt"],
                       "bio": "I Like Rock Music",
                       "DOB": None,
                       "location": None
                   }):
            resp = c.get("/user")
            assert resp.status_code == 200
            assert "Sebastian" in resp.text
            assert "sebastiantest" in resp.text
            assert "Test" in resp.text
            assert "Pages Authored" in resp.text
            assert "test1.txt" in resp.text and "test2.txt" in resp.text
            assert "Bio" in resp.text and "I Like Rock Music" in resp.text
            assert not "Date of Birth" in resp.text
            assert not "Location" in resp.text


def test_user_POST_redirects_TRUE(app2, client2):
    user = User("Sebastian")
    with app2.test_client(user=user) as c:
        with patch("flaskr.backend.Backend.get_user_info",
                   return_value={
                       "username": "sebastiantest",
                       "first_name": "Sebastian",
                       "last_name": "Test",
                       "pages_authored": ["test1.txt", "test2.txt"],
                       "bio": "I Like Rock Music",
                       "DOB": None,
                       "location": None
                   }):
            resp = c.post("/user", follow_redirects=True)
            print(resp.text)
            assert "Write a brief description" in resp.text
            assert resp.status_code == 200  # Means it already redirected to home
            # Already redirected because follow_redirects=True


def test_edit_user_information_GET(app2, client2):
    user = User("sebastiantest")
    with app2.test_client(user=user) as c:
        with patch("flaskr.backend.Backend.get_user_info",
                   return_value={
                       "username": "sebastiantest",
                       "first_name": "Sebastian",
                       "last_name": "Test",
                       "pages_authored": ["test1.txt", "test2.txt"],
                       "bio": "I Like Rock Music",
                       "DOB": None,
                       "location": None
                   }):
            resp = c.get("/edit_info")
            print(resp.text)
            assert resp.status_code == 200
            assert "I Like Rock Music" in resp.text
            assert "Date of Birth" in resp.text
            assert "Location" in resp.text
            assert not "Pages Authored" in resp.text
            assert "Update Profile Information"
            assert not "Sebastian" in resp.text
            assert not "Test" in resp.text


def test_edit_user_info_POST_redirects_TRUE(app2, client2):
    user = User("Sebastian")
    with app2.test_client(user=user) as c:
        with patch("flaskr.backend.Backend.get_user_info",
                   return_value={
                       "username": "sebastiantest",
                       "first_name": "Sebastian",
                       "last_name": "Test",
                       "pages_authored": ["test1.txt", "test2.txt"],
                       "bio": "I Like Rock Music",
                       "DOB": None,
                       "location": None
                   }):
            with patch("flaskr.backend.Backend.update_user_info"):
                resp = c.post("/edit_info",
                              data={
                                  "bio": "test",
                                  "DOB": "None",
                                  "location": "None"
                              },
                              follow_redirects=True)
                assert resp.status_code == 200  # already redirected to user page
                assert "Sebastian" in resp.text
                assert "sebastiantest" in resp.text
                assert "Test" in resp.text
                assert "Pages Authored" in resp.text
                assert "test1.txt" in resp.text and "test2.txt" in resp.text


def test_user_POST_redirects_FALSE(app2, client2):
    user = User("Sebastian")
    with app2.test_client(user=user) as c:
        with patch("flaskr.backend.Backend.get_user_info",
                   return_value={
                       "username": "sebastiantest",
                       "first_name": "Sebastian",
                       "last_name": "Test",
                       "pages_authored": ["test1.txt", "test2.txt"],
                       "bio": "I Like Rock Music",
                       "DOB": None,
                       "location": None
                   }):
            with patch("flaskr.backend.Backend.update_user_info"):
                resp = c.post("/edit_info",
                              data={
                                  "bio": "test",
                                  "DOB": "None",
                                  "location": "None"
                              },
                              follow_redirects=False)
                assert "Redirecting" in resp.text  # currently redirecting because follow_redirects = False
                assert resp.status_code == 302  # should be 302 because we should be redirecting to edit profile information page


''' NEW FIXTURES FOR UPLOAD '''


@pytest.fixture
def mock_backend():
    return MagicMock()


@pytest.fixture
def app3(mock_backend):
    app3 = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    }, mock_backend)
    return app3


@pytest.fixture
def client3(app3):
    app3.test_client_class = FlaskLoginClient
    return app3.test_client(app3.test_client_class)


''' Tests the GET method of the /upload route. Makes sure that the user is logged in to upload and it makes sure that it calls the upload.html form for the user to upload their file.'''


def test_upload_get(app3, client3):
    user = User("Sebastian")
    with app3.test_client(user=user) as c:
        assert user.is_anonymous == False
        resp = c.get("/upload")
        assert resp.status_code == 200
        expected = render_template("upload.html", user=user)
        assert expected == resp.text


''' Tests the POST method of the /upload route. Makes sure that the user is logged in to upload and it makes sure that after the user uploads the file, it reroutes back to the Pages page.'''


def test_upload_post(mock_backend, app3, client3):

    file1 = MagicMock()
    file1.name = "test1.txt"

    file2 = MagicMock()
    file2.name = "test2.txt"

    user = User("Sebastian")
    with app3.test_client(user=user) as c:
        mock_backend.upload.return_value = "Passed"
        mock_backend.get_all_page_names.return_value = [file1, file2]
        resp = c.post("/upload",
                      follow_redirects=True,
                      data=dict(file=(io.BytesIO(b"this is a test"),
                                      'test.txt')))
        mock_backend.upload.assert_called_once()
        #print(resp.text)
        assert resp.status_code == 200
        assert "Pages contained in this Wiki" in resp.text


''' Tests the GET method of the /reupload route. Makes sure that the user is logged in to reupload and it makes sure that it calls the reupload.html form for the user to upload their file.'''


def test_reupload_get(app3, client3):
    user = User("Sebastian")
    with app3.test_client(user=user) as c:
        assert user.is_anonymous == False
        resp = c.get("/reupload")
        assert resp.status_code == 200
        expected = render_template("reupload.html", user=user)
        assert expected == resp.text


''' Tests the POST method of the /reupload route. Makes sure that the user is logged in to upload and it makes sure that after the user uploads the file, it reroutes back to the Pages page.'''


def test_reupload_post(mock_backend, app3, client3):

    file1 = MagicMock()
    file1.name = "test1.txt"

    file2 = MagicMock()
    file2.name = "test2.txt"

    user = User("Sebastian")
    with app3.test_client(user=user) as c:
        mock_backend.upload.return_value = "Passed"
        mock_backend.get_all_page_names.return_value = [file1, file2]
        resp = c.post("/reupload",
                      follow_redirects=True,
                      data=dict(file=(io.BytesIO(b"this is a test"),
                                      'test.txt')))
        mock_backend.upload.assert_called_once()
        #print(resp.text)
        assert resp.status_code == 200
        assert "Pages contained in this Wiki" in resp.text
