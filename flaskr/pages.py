from flask import render_template, redirect, flash, url_for
from flask import Flask
from flask_login import login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flaskr.user import User

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=25)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=25)])
    submit = SubmitField("Submit")

def make_endpoints(app, backend):
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        wiki_page = backend.get_wiki_page("test.txt")
        return render_template("home.html", wiki_page = wiki_page, user=current_user)

    @app.route("/pages")
    def pages():
        pages = backend.get_all_page_names()
        return render_template("pages.html", pages = pages, user=current_user)

    @app.route("/pages/<pageName>")
    def page(pageName):
        # content = backend.get_wiki_page(pageName)
        # TODO: pass content=content once the backend class is up
        return render_template("page_Content.html", content = content, user=current_user)


    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route("/login", methods=["POST", "GET"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            #do backend stuff
            # check if backend stuff went well
            # if backend stuff went well, then
            user = User(form.username.data)
            login_user(user, remember=True)
            return redirect(url_for('home'))
        return render_template("login.html", form=form, user=current_user)
    
    @app.route("/signup", methods=["POST", "GET"])
    def sign_up():
        return "Sign Up"


    @app.route("/logout", methods=["POST", "GET"])
    def log_out():
        logout_user()
        return redirect(url_for('home'))

    
    