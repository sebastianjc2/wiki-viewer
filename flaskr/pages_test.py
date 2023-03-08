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
    with patch("flaskr.backend.Backend.get_all_page_names", return_value=[file1, file2]):
        resp = client.get("/pages")
        #print(resp.data)
        assert resp.status_code == 200
        assert b"Pages contained in this Wiki" in resp.data
        assert b"bla" in resp.data
        assert b"test" in resp.data

def test_individual_page(client):
    file1 = "Ataxia was a short-lived American experimental rock supergroup formed in 2004 by guitarist John Frusciante (Red Hot Chili Peppers), bassist Joe Lally (Fugazi) and drummer Josh Klinghoffer (Dot Hacker, The Bicycle Thief), who later succeeded Frusciante as the lead guitarist of the Red Hot Chili Peppers until 2019, at which point Frusciante rejoined the band. Ataxia wrote and recorded songs for two weeks, and the material was separated into two albums: Automatic Writing (2004) and AW II (2007). The songs all feature a ground-bass line with the guitar overlaying different motifs and long developments."
    with patch("flaskr.backend.Backend.get_wiki_page", return_value=file1):
        resp = client.get("/pages/Ataxia")
        assert resp.status_code == 200
        #print(resp.data.decode("utf-8"))
        assert file1 in resp.data.decode("utf-8")

def test_individual_page_routing(client):
    file1 = "This is a test file"
    page_name = "test"

    with patch("flaskr.backend.Backend.get_wiki_page", return_value=file1):
        resp = client.get("/pages/<page_name>")
        assert resp.status_code == 200
        print(resp.data.decode("utf-8"))
        assert file1 in resp.data.decode("utf-8")

def test_upload():
    pass


# continue with this one still
# def test_individual_pages(client, pageName):
#     resp = client.get("/pages/<pageName>")
#     assert resp.status_code == 200






''' NEW FIXTURES FOR LOGIN RELATED TESTS'''

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

def test_navbar_and_home_page_change_when_logged_in(app2, client2):
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
        assert "Login" in expected and "Login" in resp.text
        # assert expected == resp.text


def test_login_post_redirects_TRUE(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in", return_value = "Passed"):
            resp = c.post("/login", data={"csrf_token":"Ignore",
                                                "username":"Bob",
                                                "password":"test1234",
                                                "submit":"Login"}, follow_redirects=True)                                                
            assert "Bob" in resp.text
            assert resp.status_code == 200 # Means it already redirected to home
            # Already redirected because follow_redirects=True
            

def test_login_post_auto_redirects_FALSE(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in", return_value = "Passed"):
            resp = c.post("/login", data={"csrf_token":"Ignore",
                                                "username":"Bob",
                                                "password":"test1234",
                                                "submit":"Login"}, follow_redirects=False)

            assert "Redirecting" in resp.text
            assert resp.status_code == 302 # Mean's its in the process of redirecting
            # Hasn't redirected yet because follow_redirects=False
            

def test_login_post_wrong_password(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in", return_value = "Password fail"):
            resp = c.post("/login", data={"csrf_token":"Ignore",
                                            "username":"Bob",
                                            "password":"test1234",
                                            "submit":"Login"})
            assert resp.text == "Password is incorrect." 


def test_login_post_non_existing_username(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_in", return_value = "Username Fail"):
            resp = c.post("/login", data={"csrf_token":"Ignore",
                                            "username":"Bob",
                                            "password":"test1234",
                                            "submit":"Login"})
            assert resp.text == "That username does not exist." 


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

def test_signup_post_redirects_TRUE(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_up", return_value = "Success"):
            resp = c.post("/signup", data={"csrf_token":"Ignore",
                                                "username":"Bob",
                                                "password":"test1234",
                                                "submit":"Login"}, follow_redirects=True)                                                
            assert "Bob" in resp.text
            assert resp.status_code == 200 # Means it already redirected to home
            # Already redirected because follow_redirects=True

def test_signup_post_auto_redirects_FALSE(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_up", return_value = "Success"):
            resp = c.post("/signup", data={"csrf_token":"Ignore",
                                                "username":"Bob",
                                                "password":"test1234",
                                                "submit":"Login"}, follow_redirects=False)

            assert "Redirecting" in resp.text
            assert resp.status_code == 302 # Mean's its in the process of redirecting
            # Hasn't redirected yet because follow_redirects=False

def test_signup_post_username_already_taken(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_up", return_value = "Username is taken."):
            resp = c.post("/signup", data={"csrf_token":"Ignore",
                                            "username":"Bob",
                                            "password":"test1234",
                                            "submit":"Login"})
            assert resp.text == "That username is already taken." 

def test_signup_post_invalid_characters(app2, client2):
    with client2 as c:
        with patch("flaskr.backend.Backend.sign_up", return_value = "Invalid characters in username."):
            resp = c.post("/signup", data={"csrf_token":"Ignore",
                                            "username":"Bob",
                                            "password":"test1234",
                                            "submit":"Login"})
            assert resp.text == "Invalid characters in username." 

    
def test_log_out(app2, client2):
    user=User("Sebastian")
    assert user.is_anonymous == False
    with app2.test_client(user=user) as c:
        resp = c.get("/logout")
        assert resp.status_code == 302 # should be 302 because we should be redirecting to home page
        assert current_user.is_anonymous == True # should be True now, since we are being logged out    


def test_log_out_redirects_TRUE(app2, client2):
    user=User("Sebastian")
    assert user.is_anonymous == False
    with app2.test_client(user=user) as c:
        resp = c.post("/logout", follow_redirects=True)
        assert resp.status_code == 200 # should be 200 because redirects are on, so we should be at the home page now
        assert current_user.is_anonymous == True # should be True now, since we are being logged out    
        assert "Welcome to the Wiki!" in resp.text # should be True because we should have been redirected to the home page