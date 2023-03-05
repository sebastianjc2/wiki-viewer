# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
#from flask_sqlalchemy import SQLALchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import pages
import io
from io import BytesIO
import pandas 


#bcrypt = Bcrypt(app)


class Backend:

    def __init__(self):
        self.storage_client = storage.Client()
        self.wiki_content_bucket = self.storage_client.bucket("wiki-content")
        self.users_passwords_bucket = self.storage_client.bucket("users_passwords")
        
    def get_wiki_page(self, pageName):
        blob = self.wiki_content_bucket.get_blob(pageName)
        with blob.open("r") as f:
            return f.read()

    def get_all_page_names(self):
        blobs = self.storage_client.list_blobs("wiki-content")
        return blobs

    def upload(self, file):
        #class UploadFileForm(FlaskForm):
            #file = FileField("File", validators=[InputRequired])
            #submit = SubmitField("Upload File")
        #form = UploadFileForm()
        #if form.validate_on_submit():
        #file = form.file.data
        blob = self.wiki_content_bucket.blob(file.filename)
        blob.upload_from_file(file)

    def sign_up(self, user, password):
        
        #hashed_password = bcrypt.generate_password_hash(password)
        #new_user = str(form.username.data) + "," + str(hashed_password)
        #blob = self.users_passwords_bucket.blob("user_passwords")
        #with blob.open("a") as f:
                #f.write(new_user + "\n")
        #return redirect(url_for('login'))
        blob = self.users_passwords_bucket.blob(user + '.txt')
        if blob.exists(self.storage_client):
            return False
        else:
            with blob.open('w') as f:
                f.write(password)
            return True
        

    def sign_in(self, user, password):
        #form = pages.LoginForm
        blob = self.users_passwords_bucket.blob(user + '.txt')
        if blob.exists(self.storage_client):
            with blob.open('r') as f:
                if f.read() == password:
                    return "Passed"
                else:
                    return "Password fail"
        else:
            return "Username Fail"
        pass

    def get_image(self):
        pass

