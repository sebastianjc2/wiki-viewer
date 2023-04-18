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
    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=25)])
    submit = SubmitField(label="Login")


class SignupForm(FlaskForm):
    first_name = StringField(
        validators=[InputRequired(), Length(min=2, max=25)])
    last_name = StringField(validators=[InputRequired(), Length(min=2, max=25)])
    username = StringField(validators=[InputRequired(), Length(min=3, max=25)])
    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=25)])
    submit = SubmitField(label="Sign Up")


class Upload:
    UPLOAD_FOLDER = '/path/to/the/uploads'
    ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in Upload().ALLOWED_EXTENSIONS


def make_endpoints(app, backend):
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    ''' This will be the home page template, the default template that gets shown when you enter the wiki '''

    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        return render_template("home.html", user=current_user)

    ''' This will be the about page, and our function uses backend.get_image to get all 3 of our images from the buckets, and include them in this page.
    This will get called with /about in the url '''

    @app.route("/about")
    def about():
        chris_image_type, chris_image = backend.get_image('Chris.jpg', "about")
        sebastian_image_type, sebastian_image = backend.get_image(
            'Sebastian.jpg', "about")
        chelsea_image_type, chelsea_image = backend.get_image(
            'Chelsea.jpg', "about")
        return render_template("about.html",
                               user=current_user,
                               chris_image_type=chris_image_type,
                               chris=chris_image,
                               sebastian_image_type=sebastian_image_type,
                               sebastian=sebastian_image,
                               chelsea_image_type=chelsea_image_type,
                               chelsea=chelsea_image)

    ''' This will be the Pages page, and our function uses backend.get_all_page_names to get all the page names of the text files included in the content bucket.
    This will get called with /pages in the url and renders the pages.html template'''

    @app.route("/pages", methods=["POST", "GET"])
    def pages():
        pages = backend.get_all_page_names()
        if current_user.is_authenticated:
            user_favs = backend.get_favorites_list(user=current_user)

        if request.method == 'POST':
            page_name = request.form['page_name']
            edit_type = request.form['edit_type']

            if edit_type == "add":
                backend.add_favorite(user=current_user, page_name=page_name)
            elif edit_type == "remove":
                backend.remove_favorite(user=current_user, page_name=page_name)

        #TODO: when you refresh the page, the hearts are unhearted. make sure that when you refresh, the hearts stay hearted.
        #TODO(for teammate): add the favorites list with the hearts under the title "Favorites List"

        if current_user.is_authenticated:
            return render_template("pages.html",
                                   pages=pages,
                                   user=current_user,
                                   favorites=user_favs)
        else:
            return render_template("pages.html", pages=pages, user=current_user)

    ''' This function routes to the specific individual wiki pages with band content in them, and it uses backend.get_wiki_page to get all the content from the bucket for this specific wiki page.
    This will get called with /pages/<pagename> in the url and renders the pages_Content.html template'''

    @app.route("/pages/<pageName>")
    def page(pageName):
        page_name = pageName + ".txt"
        content = backend.get_wiki_page(page_name)
        return render_template("page_Content.html",
                               content=content,
                               page_name=pageName,
                               user=current_user)

    ''' This will be the login page. This will get called with /login in the url and renders the login.html template
    We use LoginForm to collect the username and password and show the fields on the page, once it is submitted it uses 
    backend.sign_in with that username and password and make sure it matches the info for an existing user, and if it does,
    it logs the user in and redirects them to the home page.'''

    @app.route("/login", methods=["POST", "GET"])
    def login():
        form = LoginForm()
        # print("outside if")
        # print(form.is_submitted())

        if form.validate_on_submit():
            user = User(form.username.data)
            sign_in_status = backend.sign_in(form.username.data,
                                             form.password.data)
            if sign_in_status == "Passed":
                # print("passed")
                login_user(user, remember=True)
            elif sign_in_status == "Password fail":
                return "Password is incorrect."
            else:
                return "That username does not exist."
            return redirect(url_for('home'))
        # print(form.errors)
        # print("before render")
        return render_template("login.html", form=form, user=current_user)

    ''' This will be the sign up page. This will get called with /signup in the url and renders the login.html template
    We use SignupForm to collect the username and password and show the fields on the page, once it is submitted it uses 
    backend.sign_up with that username and password and make sure the username is valid and does not already exist. 
    If everything goes well, it logs the user in and redirects them to the home page.'''

    @app.route("/signup", methods=["POST", "GET"])
    def sign_up():
        form = SignupForm()
        if form.validate_on_submit():
            # do backend stuff
            # check if backend stuff went well
            # if it did, then:
            user = User(form.username.data)
            sign_up_status = backend.sign_up(form.first_name.data,
                                             form.last_name.data,
                                             form.username.data,
                                             form.password.data)
            if sign_up_status == "Success":
                login_user(user, remember=True)
            elif sign_up_status == "Username is taken.":
                return "That username is already taken."
            else:
                return "Invalid characters in username."
            return redirect(url_for('home'))
        return render_template("signup.html", form=form, user=current_user)

    '''This is called with the /logout route and requires the user to be logged in already. It logs out the user, and redirects them to the home page'''

    @app.route("/logout", methods=["POST", "GET"])
    @login_required
    def log_out():
        logout_user()
        return redirect(url_for('home'))

    ''' This is called with the /upload route and requires the user to be logged in already.
    The way this function works is if there is no file inputted, it will stay on the same page until the user inputs a file.
    If there is a file uploaded and its valid, but it already exists in the content bucket, it will tell the user the file already exists.
    If there is a file uploaded, the file is valid, and it does not already exist in the content bucket, it will reroute the user back to the Pages page once the file is uploaded.'''

    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file and allowed_file(file.filename):
                upload_outcome = backend.upload(file, current_user.get_id())
                if upload_outcome == "Exists":
                    return "Only the original author can reupload their pages."
                return redirect(url_for('pages'))
        return render_template("upload.html", user=current_user)

    @app.route('/reupload', methods=['GET', 'POST'])
    @login_required
    def reupload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file and allowed_file(file.filename):
                upload_outcome = backend.upload(file, current_user.get_id())
                if upload_outcome == "Exists":
                    return "Only the original author can reupload their pages."
                return redirect(url_for('pages'))
        return render_template("reupload.html", user=current_user)

    @app.route("/user", methods=["POST", "GET"])
    @login_required
    def user():
        info = backend.get_user_info(current_user.get_id())
        if request.method == "POST":
            return redirect(url_for('edit_user_information'))
        return render_template("user.html", info=info, user=current_user)

    @app.route("/edit_info", methods=["POST", "GET"])
    @login_required
    def edit_user_information():
        if request.method == "POST":
            bio = request.form["bio"]
            dob = request.form["DOB"]
            location = request.form["location"]
            backend.update_user_info(current_user.get_id(), bio, dob, location)
            return redirect(url_for('user'))
        info = backend.get_user_info(current_user.get_id())
        return render_template("edit_user_info.html",
                               info=info,
                               user=current_user)
