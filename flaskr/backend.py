# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.utils import secure_filename
import hashlib
from google.api_core.exceptions import NotFound
import google.cloud
from google.cloud import exceptions
from flaskr.pages import Upload
from io import BytesIO
from PIL import Image
import base64
import json


class Backend:

    #Initializing the storage client and the buckets, uses an automatic assignment
    #that lets the storage client to be assigned normally if not specified, but allows
    #mocking if the storage_client argument is filled using a magicmock object.
    def __init__(self, storage_client=storage.Client()):
        self.storage_client = storage_client
        self.wiki_content_bucket = self.storage_client.bucket("wiki-content")
        self.users_passwords_bucket = self.storage_client.bucket(
            "users_passwords")
        self.images_about_bucket = self.storage_client.bucket("images_about")
        self.users_info_bucket = self.storage_client.bucket("users_profiles")

    #Returns a page from the wiki content bucket
    def get_wiki_page(self, pageName):
        blob = self.wiki_content_bucket.get_blob(pageName)
        with blob.open("r") as f:
            raw = f.read()
            info = json.loads(raw)
            return info["content"]

    #Returns a list of all the files uploaded to the wiki-content bucket
    def get_all_page_names(self):
        blobs = self.storage_client.list_blobs("wiki-content")
        return blobs

    #Takes a file and uploads it to cloud storage if it doesn't already exist or if the user is the author of that existing page.
    def upload(self, file_up, username):
        #Creates a blob
        blob = self.wiki_content_bucket.blob(file_up.filename)
        #Checks if it already exists
        if blob.exists(self.storage_client):
            with blob.open("r") as f:
                raw = f.read()
                info = json.loads(raw)
            #If it does, we check the author
            if info["author"] != username:
                #If the original author isnt the one trying to reupload it, it will return early.
                #Otherwise, it will continue.
                return "Exists"
            else:
                #In the case
                blob.upload_from_file(file_up)
                with blob.open("r") as f:
                    content = f.readlines()
                with blob.open("w") as f:
                    modified = []
                    for line in content:
                        modified.append(line.strip())
                    content_and_author = {
                        "content": modified,
                        "author": username
                    }
                    f.write(json.dumps(content_and_author, indent=2))
                return "Passed"
        else:
            #Else, upload and then return
            blob.upload_from_file(file_up)

            with blob.open("r") as f:
                content = f.readlines()
            with blob.open("w") as f:
                modified = []
                for line in content:
                    modified.append(line.strip())
                content_and_author = {"content": modified, "author": username}
                f.write(json.dumps(content_and_author, indent=2))

            user = self.users_info_bucket.blob(username + '.txt')
            with user.open("r") as f:
                data = f.read()
                info = json.loads(data)
            with user.open("w") as f:
                info["pages_authored"].append(file_up.filename)
                data = json.dumps(info)
                f.write(data)
            return "Passed"

    #Creates a new user, saved as a txt file with a hashed password inside
    def sign_up(self, first_name, last_name, user, password):
        # Generated random key with secrets.token_hex()
        secret_key = '5cfdb0b2f0177067d707306d43820b1bd479a558ad5ce7eac645cb77f8aacaa1'
        #Checks if these handful of characters (space, comma, backslash, forwardslash)
        #are in the inputted username, and returns if so, since those are the characters
        #we deemed invalid for clarity's sake.
        if " " in user or "," in user or "\\" in user or "/" in user:
            return "Invalid characters in username."
        blob = self.users_passwords_bucket.blob(user + '.txt')
        blob2 = self.users_info_bucket.blob(user + '.txt')
        #Adds 'salt' to the password before hashing to make it so two people with the same
        #password don't have the same hash. The secret key also helps to further obscure the data.
        with_salt = f"{user}{secret_key}{password}"
        #Hashes the password for storage
        password = hashlib.blake2b(with_salt.encode()).hexdigest()
        #Checks if someone already has that username by checking for that filename in the bucket
        #If so it returns early
        if blob.exists(self.storage_client):
            return "Username is taken."
        #Otherwise, it writes the password to the file.
        else:
            with blob2.open('w') as f:
                user_dict = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": user,
                    "pages_authored": [],
                    "favorites": [],
                    "bio": None,
                    "DOB": None,
                    "location": None
                }
                data = json.dumps(user_dict)
                f.write(data)

            with blob.open('w') as f:
                f.write(password)
            return "Success"

    def sign_in(self, user, password):
        #Generated random key with secrets.token_hex()
        #Same secret key used in sign up so the sign in works properly
        secret_key = '5cfdb0b2f0177067d707306d43820b1bd479a558ad5ce7eac645cb77f8aacaa1'
        #Adds all the same 'salt' to the password before hashing so the outcome
        #will be the same as when signing up (if its the same password)
        with_salt = f"{user}{secret_key}{password}"
        password = hashlib.blake2b(with_salt.encode()).hexdigest()

        blob = self.users_passwords_bucket.blob(user + '.txt')
        #Checks if the user exists
        if blob.exists(self.storage_client):
            #Reads the blob and compares the hashed password saved there
            #to the one input and hashed in this method
            with blob.open('r') as f:
                #If theyre the same, it passes
                if f.read() == password:
                    return "Passed"
                #Otherwise, fails.
                else:
                    return "Password fail"
        else:
            #If the user doesnt exist, fails.
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

    def get_user_info(self, username):
        user = self.users_info_bucket.blob(username + '.txt')
        with user.open("r") as f:
            data = f.read()
            info = json.loads(data)
        return info

    def helper_update_user_info(self, username, bio, dob, location):
        # getting user info
        info = self.get_user_info(username)

        # updating the user info
        info["bio"] = bio
        info["DOB"] = dob
        info["location"] = location
        data = json.dumps(info)
        return data

    def update_user_info(self, username, bio, dob, location):
        user = self.users_info_bucket.blob(username + '.txt')
        data = self.helper_update_user_info(username, bio, dob, location)
        with user.open("w") as f:
            f.write(data)
        return

    def get_favorites_list(self, user):
        user_blob = self.users_info_bucket.blob(user.name + '.txt')
        with user_blob.open("r") as f:
            data = f.read()
            info = json.loads(data)
        return info['favorites']

    def helper_update_favorites_list(self, user, page_name, edit_type):
        info = self.get_user_info(user.name)

        if edit_type == "add":
            if page_name not in info['favorites']:
                info['favorites'].append(page_name)
                info['favorites'].sort()

        elif edit_type == "remove":
            if page_name in info['favorites']:
                info['favorites'].remove(page_name)
                info['favorites'].sort()

        data = json.dumps(info)
        return data

    def add_favorite(self, user, page_name):
        user_blob = self.users_info_bucket.blob(user.name + '.txt')
        data = self.helper_update_favorites_list(user, page_name, 'add')
        with user_blob.open("w") as f:
            f.write(data)
        return

    def remove_favorite(self, user, page_name):
        user_blob = self.users_info_bucket.blob(user.name + '.txt')
        data = self.helper_update_favorites_list(user, page_name, 'remove')
        with user_blob.open("w") as f:
            f.write(data)
        return
