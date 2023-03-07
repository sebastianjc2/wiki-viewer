from flaskr import create_app
from flask import render_template
from flaskr import pages
from flaskr import Backend
from unittest.mock import MagicMock, patch
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
def test_home_page(client):
    resp = client.get("/")
    print(resp.data)
    assert resp.status_code == 200
    assert b"Welcome to the Wiki" in resp.data

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

# TODO(Project 1): Write tests for other routes.
# def test_about(client):
#     resp = client.get("/about")
#     expected = render_template("about.html")

#     assert resp.status_code == 200
#     assert expected == resp.data