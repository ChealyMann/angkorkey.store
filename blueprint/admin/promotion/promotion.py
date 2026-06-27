import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from form.PromotionForm import PromotionForm, PromotionFormEdit
from models import Promotion
from extensions import db
from upload_service import save_image

promotion_bp = Blueprint('promotion', __name__)

# ============================================================
# Helper
# ============================================================
def delete_promotion_image(filename):
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
                print(f"Error deleting promotion image file {path}: {e}")

# ============================================================
# Routes
# ============================================================
@promotion_bp.route('/admin/promotion')
def promotion():
    promotions = Promotion.query.all()
    return render_template('backend/admin/pages/promotion/promotion.html', promotions=promotions)


@promotion_bp.route('/admin/promotion/add', methods=['GET', 'POST'])
def promotion_add():
    form = PromotionForm()
    
    if form.validate_on_submit():
        unique_filename = 'none.jpg'
        
        if form.image.data:
            # FIX: Bulletproof config lookup
            allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'avif'})
            upload_dir = current_app.config.get("UPLOAD_FOLDER", "static/images")
            
            unique_filename = save_image(form.image.data, upload_dir, allowed_exts)
        
        promotion = Promotion(
            image=str(unique_filename),
            title=form.title.data,
            subtitle=form.subtitle.data,
            link=form.link.data,
            button_text=form.button_text.data,
            is_active=form.is_active.data
        )
        db.session.add(promotion)
        db.session.commit()
        
        flash('Promotion Added Successfully', 'success')
        return redirect(url_for('promotion.promotion'))
        
    return render_template('backend/admin/pages/promotion/add.html', form=form)


@promotion_bp.route('/admin/promotion/edit/<int:promotion_id>', methods=['GET', 'POST'])
def promotion_edit(promotion_id):
    promotion = Promotion.query.get_or_404(promotion_id)
    form = PromotionFormEdit()
    
    if form.validate_on_submit():
        if form.image.data:
            # Safely delete old image
            delete_promotion_image(promotion.image)
            
            # FIX: Bulletproof config lookup
            allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'avif'})
            upload_dir = current_app.config.get("UPLOAD_FOLDER", "static/images")
            
            promotion.image = save_image(form.image.data, upload_dir, allowed_exts)
        
        promotion.title = form.title.data
        promotion.subtitle = form.subtitle.data
        promotion.link = form.link.data
        promotion.button_text = form.button_text.data
        promotion.is_active = form.is_active.data
        
        db.session.commit()
        flash('Promotion Updated Successfully', 'success')
        return redirect(url_for('promotion.promotion'))
    
    if request.method == 'GET':
        form.title.data = promotion.title
        form.subtitle.data = promotion.subtitle
        form.link.data = promotion.link
        form.button_text.data = promotion.button_text
        form.is_active.data = promotion.is_active
        
    return render_template('backend/admin/pages/promotion/edit.html', form=form, promotion=promotion)


@promotion_bp.route('/admin/promotion/delete/<int:promotion_id>', methods=['GET', 'POST'])
def promotion_delete(promotion_id):
    try:
        promotion = Promotion.query.get_or_404(promotion_id)
        
        # Safely clean up image files before deleting
        delete_promotion_image(promotion.image)
        
        db.session.delete(promotion)
        db.session.commit()
        flash('Promotion Deleted Successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting promotion: {e}")
        flash('Error deleting promotion', 'danger')
        
    return redirect(url_for('promotion.promotion'))