import os
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
import uuid


def save_picture(form_picture):
    random_hex = uuid.uuid4().hex
    filename = random_hex + ".webp"
    
    picture_path = os.path.join(current_app.root_path, 'static/images', filename)
    resized_path = os.path.join(current_app.root_path, 'static/images', 'resized_' + filename)
    thumb_path = os.path.join(current_app.root_path, 'static/images', 'thumb_' + filename)

    img = Image.open(form_picture)

    # Convert to RGB if it's RGBA to avoid transparency overhead (optional)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Save original WebP image
    img.save(picture_path, 'WEBP', quality=85, method=0, optimize=False)

    # Save resized WebP for product listings
    resized_img = img.copy()
    resized_img.thumbnail((800, 800))
    resized_img.save(resized_path, 'WEBP', quality=75, method=0, optimize=False)

    # Save thumb WebP for small grids
    thumb_img = img.copy()
    thumb_img.thumbnail((100, 100))
    thumb_img.save(thumb_path, 'WEBP', quality=60, method=0, optimize=False)

    return filename