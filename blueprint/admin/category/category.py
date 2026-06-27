import os
from sqlite3 import DatabaseError
from flask import Blueprint, render_template, redirect, flash, url_for, current_app
from extensions import db
from form.CategoryForm import CategoryForm
from models import Category
from upload_service import save_image

category_bp = Blueprint('category', __name__)

# ============================================================
# Helper
# ============================================================
def delete_category_image(filename):
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
                print(f"Error deleting category image file {path}: {e}")

# ============================================================
# Routes
# ============================================================
@category_bp.route('/admin/category')
def admin_category():
    categories = Category.query.all()
    return render_template('backend/admin/pages/category/category.html', categories=categories)


@category_bp.route('/admin/category/add', methods=['GET', 'POST'])
def admin_category_add():
    form = CategoryForm()
    filename = "none.jpg"
    
    if form.validate_on_submit():
        if form.image.data:
            # FIX: Bulletproof config lookup
            allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'avif'})
            upload_dir = current_app.config.get("UPLOAD_FOLDER", "static/images")
            
            filename = save_image(form.image.data, upload_dir, allowed_exts)
            
        category = Category(
            image=str(filename),
            name=form.name.data,
            desc=form.desc.data,
            status=form.status.data
        )
        db.session.add(category)
        db.session.commit()
        
        flash('Category has been added successfully!', 'success')
        return redirect(url_for('category.admin_category'))

    return render_template('backend/admin/pages/category/add.html', form=form)


@category_bp.route('/admin/category/edit/<int:category_id>', methods=['GET', 'POST'])
def admin_category_edit(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    
    if form.validate_on_submit():
        if form.image.data:
            # Safely delete the old image using the new helper
            delete_category_image(category.image)

            # FIX: Bulletproof config lookup
            allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'avif'})
            upload_dir = current_app.config.get("UPLOAD_FOLDER", "static/images")

            category.image = save_image(form.image.data, upload_dir, allowed_exts)

        category.name = form.name.data.strip()
        category.desc = form.desc.data.strip()
        category.status = form.status.data.strip()
        
        db.session.commit()
        flash('Category has been updated successfully!', 'success')
        return redirect(url_for('category.admin_category'))
            
    if not form.is_submitted():
        form.desc.data = category.desc
        form.name.data = category.name
        form.status.data = category.status
        
    return render_template('backend/admin/pages/category/edit.html', category=category, form=form, os=os)


@category_bp.route('/admin/category/delete/<int:category_id>', methods=['POST'])
def admin_category_delete(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        
        # Safely clean up the images when category is deleted
        delete_category_image(category.image)
        
        db.session.delete(category)
        db.session.commit()
        
        flash('Category has been deleted successfully!', 'success')
        return redirect(url_for('category.admin_category'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting category: {e}")
        flash('Error deleting category', 'danger')
        return redirect(url_for('category.admin_category'))