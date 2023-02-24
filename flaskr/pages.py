from flask import render_template
from flask import Flask


def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template("main.html")

    @app.route("/pages")
    def pages():
        return render_template("pages.html")

    @app.route("/pages/redHotChiliPeppers")
    def redHotChiliPeppers():
        return render_template("main.html")

    @app.route("/pages/nirvana")
    def nirvana():
        return render_template("main.html")
    
    @app.route("/pages/deftones")
    def deftones():
        return render_template("main.html")

    # TODO(Project 1): Implement additional routes according to the project requirements.
