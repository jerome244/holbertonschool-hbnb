import os
from werkzeug.utils import secure_filename
from uuid import uuid4
from flask import current_app


def save_photo(photo_file):
    """Save uploaded photo_file to the upload folder and return its filename."""
    filename = secure_filename(photo_file.filename)
    unique_name = f"{uuid4().hex}_{filename}"

    upload_folder = os.path.join(current_app.root_path, "static/uploads")
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, unique_name)
    photo_file.save(file_path)

    return unique_name
