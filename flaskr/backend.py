# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.utils import secure_filename
import hashlib
from flaskr.pages import Upload
from io import BytesIO
from PIL import Image
import base64



class Backend:

    def __init__(self, storage_client=storage.Client()):
        self.storage_client = storage_client
        self.wiki_content_bucket = self.storage_client.bucket("wiki-content")
        self.users_passwords_bucket = self.storage_client.bucket("users_passwords")
        self.images_about_bucket = self.storage_client.bucket("images_about")
        
    def get_wiki_page(self, pageName):
        blob = self.wiki_content_bucket.get_blob(pageName)
        with blob.open("r") as f:
            return f.read()

    def get_all_page_names(self):
        blobs = self.storage_client.list_blobs("wiki-content")
        return blobs

    def upload(self, file):
        blob = self.wiki_content_bucket.blob(file.filename)
        blob.upload_from_file(file)

    def sign_up(self, user, password):
        secret_key = '5cfdb0b2f0177067d707306d43820b1bd479a558ad5ce7eac645cb77f8aacaa1'
        if " " in user or "," in user or "\\" in user or "/" in user:
            return "Invalid characters in username."
        blob = self.users_passwords_bucket.blob(user + '.txt')
        with_salt = f"{user}{secret_key}{password}"
        password = hashlib.blake2b(with_salt.encode()).hexdigest()
        if blob.exists(self.storage_client):
            return "Username is taken."
        else:
            with blob.open('w') as f:
                f.write(password)
            return "Success"
        

    def sign_in(self, user, password):
        secret_key = '5cfdb0b2f0177067d707306d43820b1bd479a558ad5ce7eac645cb77f8aacaa1'
        with_salt = f"{user}{secret_key}{password}"
        password = hashlib.blake2b(with_salt.encode()).hexdigest()

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

    def get_image(self, image, page="pages"):
        if page == "about":
            blob = self.images_about_bucket.get_blob(image)
            content = blob.download_as_bytes()
            img = base64.b64encode(content).decode("utf-8")
            content_type = blob.content_type
        else:
            blob = self.wiki_content_bucket.get_blob(image)
            content = blob.download_as_bytes()
            img = base64.b64encode(content).decode("utf-8")
            content_type = blob.content_type
        return content_type, img