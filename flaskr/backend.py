# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage

class Backend:

    def __init__(self):
        pass
        
    def get_wiki_page(self, name):
        bucket = storage.Client().bucket("wiki-content")
        blob = bucket.get_blob(name)
        with blob.open() as f:
            return f.read()


    def get_all_page_names(self):
        pass

    def upload(self):
        pass

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self):
        pass

