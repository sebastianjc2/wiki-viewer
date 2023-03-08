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
import unittest
from flask_testing import TestCase

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


def test_home_page_while_logged_out(client, app):
    resp = client.get("/")
    #print(resp.data)
    assert resp.status_code == 200
    with app.app_context():
        expected = render_template("home.html", user=current_user)
        #print(expected)
        assert b"Welcome to the Wiki!" in resp.data
        assert expected == resp.data.decode("utf-8")

def test_about(client, app):
    resp = client.get("/about")
    assert resp.status_code == 200
    with app.app_context():
        expected = render_template("about.html", user=current_user)
        assert "Sebastian Caballero" in resp.text and "Sebastian Caballero" in expected
        assert "Christopher Cordero" in resp.text and "Christopher Cordero" in expected
        assert "Chelsea Garcia" in resp.text and "Chelsea Garcia" in expected

def test_pages(client):
    file1 = MagicMock()
    file1.name = "test.txt"

    file2 = MagicMock()
    file2.name = "blah.txt"
    resp = client.get("/pages")
    #print(resp.data)
    assert resp.status_code == 200
    assert b"Pages contained in this Wiki" in resp.data
    assert b"bla" in resp.data
    assert b"test" in resp.data
def test_individual_page_routing(client):
    file1 = "This is a test file"
    page_name = "test"

    resp = client.get("/pages/<page_name>")
    assert resp.status_code == 200
    print(resp.data.decode("utf-8"))
    assert file1 in resp.data.decode("utf-8")

def test_upload():
    #resp = client.get("/upload")
    #assert resp.status_code == 200


# continue with this one still
# def test_individual_pages(client, pageName):
#     resp = client.get("/pages/<pageName>")
#     assert resp.status_code == 200








#NEW FIXTURES FOR LOGIN RELATED TESTS
@pytest.fixture
def app2():
    app2 = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED':False,
    })
    return app2

@pytest.fixture
def client2(app2):
    app2.test_client_class = FlaskLoginClient
    return app2.test_client(app2.test_client_class)

def test_navbar_change_when_logged_in(app2, client2):
    user=User("Sebastian")
    with app2.test_client(user=user) as c:
        resp = c.get("/")
        assert resp.status_code == 200
        expected = render_template("home.html", user=user)
        assert "Sebastian" in expected
        assert "Welcome to the Wiki, Sebastian!" in expected
        assert "Logout" in expected
        assert expected == resp.text


def test_login_template(app2, client2):
    with app2.app_context():
        form = MagicMock()
        # form.username = '<input id="username" maxlength="25" minlength="3" name="username" required type="text" value="Bob">'
        # form.hidden_tag.return_value = '<input id="csrf_token" name="csrf_token" type="hidden" value="IjhmYzQzOGY4MDQyYmI5YmM4OWU5MTQ5YjFlMTYxOTQ3NzQ3MjYwODAi.ZAea6Q.chsyN2xGVvv9Q7RWn8RnVvcRqEs">'
        resp = client2.get("/login")
        assert resp.status_code == 200
        #print(resp.text)
        expected = render_template("login.html", form=form, user=current_user)
        #print(expected)
        assert "username" in expected and "username" in resp.text
        assert "password" in expected and "password" in resp.text
        assert "submit" in expected and "submit" in resp.text
        # assert expected == resp.text


def test_login_post2(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in", return_value = "Passed"):
            resp = c.post("/login", data={"csrf_token":"Ignore",
                                                "username":"Bob",
                                                "password":"test1234",
                                                "submit":"Login"}, follow_redirects=True)                                                
            assert "Bob" in resp.text
            assert resp.status_code == 200
            
def test_login_post_code(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in", return_value = "Passed"):
            resp = c.post("/login", data={"csrf_token":"Ignore",
                                                "username":"Bob",
                                                "password":"test1234",
                                                "submit":"Login"}, follow_redirects=False)

            assert resp.status_code == 302
            

def test_login_post3(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in", return_value = "Password fail"):
            resp = c.post("/login", data={"csrf_token":"Ignore",
                                            "username":"Bob",
                                            "password":"test1234",
                                            "submit":"Login"})
            assert resp.text == "Password is incorrect." # Means it redirected

def test_login_post4(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in", return_value = "Username Fail"):
            resp = c.post("/login", data={"csrf_token":"Ignore",
                                            "username":"Bob",
                                            "password":"test1234",
                                            "submit":"Login"})
            assert resp.text == "That username does not exist." # Means it redirected



