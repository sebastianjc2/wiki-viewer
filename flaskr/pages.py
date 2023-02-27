from flask import render_template
from flask import Flask


def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template("home.html")

    @app.route("/pages")
    def pages():
        return render_template("pages.html")

    @app.route("/pages/<pageName>")
    def page(pageName):
        # content = backend.get_wiki_page(pageName)
        # TODO: pass content=content once the backend class is up
        return render_template("main.html", content=content)

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route("/login", methods=["POST", "GET"])
    def login():
        return "Login"
    
    @app.route("/signup", methods=["POST", "GET"])
    def sign_up():
        return "Sign Up"

    @app.route("/logout", methods=["POST", "GET"])
    def log_out():
        return "Log Out"

    
    