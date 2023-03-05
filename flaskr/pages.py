from flask import render_template, redirect, flash, url_for, request
from flask import Flask
from flask_login import login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flaskr.user import User
from werkzeug.utils import secure_filename
import os

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=25)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=25)])
    submit = SubmitField(label="Login")

class SignupForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=25)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=25)])
    submit = SubmitField(label="Sign Up")

class Upload:
    UPLOAD_FOLDER = '/path/to/the/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in Upload().ALLOWED_EXTENSIONS

def make_endpoints(app, backend):
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        wiki_page = backend.get_wiki_page("test.txt")
        return render_template("home.html", wiki_page = wiki_page, user=current_user)

    @app.route("/about")
    def about():
        return render_template("about.html", user=current_user)

    @app.route("/pages")
    def pages():
        pages = backend.get_all_page_names()
        return render_template("pages.html", pages = pages, user=current_user)

    @app.route("/pages/<pageName>")
    def page(pageName):
        content = backend.get_wiki_page(pageName)
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
            sign_in_status = backend.sign_in(form.username.data, form.password.data)
            if sign_in_status == "Passed":
                login_user(user, remember=True)
            elif sign_in_status == "Password fail":
                return "Password is incorrect."
            else:
                return "That username does not exist."
            return redirect(url_for('home'))
        return render_template("login.html", form=form, user=current_user)
    
    @app.route("/signup", methods=["POST", "GET"])
    def sign_up():
        form = SignupForm()
        if form.validate_on_submit():
            # do backend stuff
            # check if backend stuff went well
            # if it did, then:
            user = User(form.username.data)
            if backend.sign_up(form.username.data, form.password.data):
                login_user(user, remember=True)
            else:
                return "That username is already taken."
            return redirect(url_for('home'))
        return render_template("signup.html", form=form, user=current_user)


    @app.route("/logout", methods=["POST", "GET"])
    def log_out():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
        # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                backend.upload(file)
                #return redirect(url_for('download_file', name=filename))         
                return redirect(url_for('pages'))       
        return render_template("upload.html", user=current_user)