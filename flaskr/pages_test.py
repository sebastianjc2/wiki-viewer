from flaskr import create_app
from flask import render_template
from flaskr import pages
from flaskr import Backend
from flaskr.user import User
from unittest.mock import MagicMock, patch
from flask_login import current_user, FlaskLoginClient, login_user, logout_user, LoginManager
import pytest

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client, app):
    resp = client.get("/")
    #print(resp.data)
    assert resp.status_code == 200
    with app.app_context():
        expected = render_template("home.html", user=current_user)
        #print(expected)
        assert b"Welcome to the Wiki" in resp.data
        assert expected == resp.data.decode("utf-8")

def test_pages(client):
    file1 = MagicMock()
    file1.name = "test.txt"

    file2 = MagicMock()
    file2.name = "blah.txt"
    with patch("flaskr.backend.Backend.get_all_page_names", return_value=[file1, file2]):
        resp = client.get("/pages")
        #print(resp.data)
        assert resp.status_code == 200
        assert b"bla" in resp.data
        assert b"test" in resp.data

# TODO(Project 1): Write tests for other routes.
def test_pages_2(client):
    resp = client.get("/pages")
    assert resp.status_code == 200
    print(resp.data)
    assert b"Pages contained in this Wiki" in resp.data

# continue with this one still
# def test_individual_pages(client, pageName):
#     resp = client.get("/pages/<pageName>")
#     assert resp.status_code == 200

@pytest.fixture
def app2():
    app2 = create_app({
        'TESTING': True,
    })
    return app2

@pytest.fixture
def client2(app2):
    app2.test_client_class = FlaskLoginClient
    return app2.test_client(app2.test_client_class)

def test_logged_in(app2, client2):
    # login_manager = LoginManager()
    # login_manager.init_app(client2)

    # @login_manager.user_loader
    # def load_user(user_id):
    #     return User(user_id)
    user=User("Sebastian")
    with app2.test_client() as c:
        # with c.session_transaction() as sess:
        #     sess['user_id'] = 'Sebastian'
        #     sess['_fresh'] = True # https://flask-login.readthedocs.org/en/latest/#fresh-logins
        
        # resp = c.get("/")
        resp = c.get("/")
        assert resp.status_code == 200
        expected = render_template("home.html", user=user)
        print(expected)
        print(resp.text)
        assert "Sebastian" in expected
        assert "Welcome to the Wiki, Sebastian!" in expected
        assert "Logout" in expected
        assert expected == resp.text

# def test_request_with_logged_in_user():
#     user = User("sebastian")
#     with app2.test_client(user=user) as client:
#         # This request has user 1 already logged in!
#         resp = client.get("/")
#         assert "Upload" in resp.data.decode("utf-8")