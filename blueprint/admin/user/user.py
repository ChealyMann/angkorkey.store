from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash
from extensions import db
from form.UserForm import UserForm, UserFormEdit
from models import User
from upload_service import save_image
import os
from sqlite3 import DatabaseError

user_bp = Blueprint('user', __name__)

# ============================================================
# Helper
# ============================================================
def delete_user_image(filename):
    if not filename or filename == "none.jpg":
        return

    paths = [
        os.path.join(current_app.root_path, "static/images", filename),
        os.path.join(current_app.root_path, "static/images", "resized_" + filename),
        os.path.join(current_app.root_path, "static/images", "thumb_" + filename),
    ]

    for path in paths:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error deleting user image file {path}: {e}")

# ============================================================
# Routes
# ============================================================
@user_bp.route('/admin/user')
def admin_user():
    users = User.query.all()
    return render_template('backend/admin/pages/user/user.html', users=users)


@user_bp.route('/admin/user/add', methods=['GET', 'POST'])
def admin_user_add():
    form = UserForm()
    filename = "none.jpg"
    
    if form.validate_on_submit():
        if form.image.data:
            # FIX: Bulletproof config lookup
            allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'avif'})
            upload_dir = current_app.config.get("UPLOAD_FOLDER", "static/images")
            
            filename = save_image(form.image.data, upload_dir, allowed_exts)
            
        phone_val = int(form.phone.data) if form.phone.data else None
        user = User(
            image=str(filename),
            username=form.username.data,
            phone=phone_val,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('User has been added successfully!', 'success')
        return redirect(url_for('user.admin_user'))
        
    return render_template('backend/admin/pages/user/add.html', form=form)


@user_bp.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
def admin_user_edit(user_id):
    form = UserFormEdit()
    user = User.query.get_or_404(user_id)
    
    if form.validate_on_submit():
        if form.image.data:
            # Safely delete the old images
            delete_user_image(user.image)

            # FIX: Bulletproof config lookup
            allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'avif'})
            upload_dir = current_app.config.get("UPLOAD_FOLDER", "static/images")

            user.image = save_image(form.image.data, upload_dir, allowed_exts)

        user.username = form.username.data.strip()
        user.phone = int(form.phone.data) if form.phone.data else None
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        db.session.commit()
        
        flash('User has been updated successfully!', 'success')
        return redirect(url_for('user.admin_user'))
            
    if not form.is_submitted():
        form.username.data = user.username
        form.phone.data = str(user.phone) if user.phone else ""
        
    return render_template('backend/admin/pages/user/edit.html', user=user, form=form, os=os)


@user_bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
def admin_user_delete(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        # Clean up images before deleting user
        delete_user_image(user.image)
        
        db.session.delete(user)
        db.session.commit()
        
        flash('User has been deleted successfully!', 'success')
        return redirect(url_for('user.admin_user'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {e}")
        flash('Error deleting user', 'danger')
        return redirect(url_for('user.admin_user'))