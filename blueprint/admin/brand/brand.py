import os

from flask import Blueprint, render_template, redirect, flash, url_for, current_app
from extensions import db
from form.BrandForm import BrandForm, BrandFormEdit
from models import Brand, Product
from upload_service import save_image

brand_bp = Blueprint("brand", __name__)


# ============================================================
# Helper
# ============================================================

def delete_brand_image(filename):
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
                print(f"Error deleting brand image file {path}: {e}")


# ============================================================
# Brand list
# ============================================================

@brand_bp.route("/admin/brand")
def brand():
    brands = Brand.query.order_by(Brand.id.desc()).all()

    return render_template(
        "backend/admin/pages/brand/brand.html",
        brands=brands,
        os=os
    )


# ============================================================
# Add brand
# ============================================================

@brand_bp.route("/admin/brand/add", methods=["GET", "POST"])
def brand_add():
    form = BrandForm()

    if form.validate_on_submit():
        try:
            exists = Brand.query.filter_by(name=form.name.data.strip()).first()

            if exists:
                flash("Brand name already exists.", "error")
                return redirect(url_for("brand.brand_add"))

            unique_filename = "none.jpg"

            if form.image.data:
                # FIX: Bulletproof config lookup
                allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'avif'})
                upload_dir = current_app.config.get("UPLOAD_FOLDER", "static/images")

                unique_filename = save_image(
                    form.image.data,
                    upload_dir,
                    allowed_exts
                )

            brand_obj = Brand(
                name=form.name.data.strip(),
                desc=form.desc.data,
                image=str(unique_filename),
                status=form.status.data
            )

            db.session.add(brand_obj)
            db.session.commit()

            flash("Brand Added Successfully", "success")
            return redirect(url_for("brand.brand"))

        except Exception as e:
            db.session.rollback()
            print("Brand Add Error:", e)
            flash("Error adding brand.", "error")
            return redirect(url_for("brand.brand_add"))

    return render_template(
        "backend/admin/pages/brand/add.html",
        form=form,
        current_image_url=None
    )


# ============================================================
# Edit brand
# ============================================================

@brand_bp.route("/admin/brand/edit/<int:brand_id>", methods=["GET", "POST"])
def brand_edit(brand_id):
    brand_obj = Brand.query.get_or_404(brand_id)
    form = BrandFormEdit()

    if form.validate_on_submit():
        try:
            exists = Brand.query.filter(
                Brand.name == form.name.data.strip(),
                Brand.id != brand_obj.id
            ).first()

            if exists:
                flash("Another brand already uses this name.", "error")
                return redirect(url_for("brand.brand_edit", brand_id=brand_obj.id))

            brand_obj.name = form.name.data.strip()
            brand_obj.desc = form.desc.data
            brand_obj.status = form.status.data

            if form.image.data:
                delete_brand_image(brand_obj.image)

                # FIX: Bulletproof config lookup
                allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'avif'})
                upload_dir = current_app.config.get("UPLOAD_FOLDER", "static/images")

                brand_obj.image = save_image(
                    form.image.data,
                    upload_dir,
                    allowed_exts
                )

            db.session.commit()

            flash("Brand Updated Successfully", "success")
            return redirect(url_for("brand.brand"))

        except Exception as e:
            db.session.rollback()
            print("Brand Edit Error:", e)
            flash("Error updating brand.", "error")
            return redirect(url_for("brand.brand_edit", brand_id=brand_obj.id))

    if brand_obj.image and brand_obj.image != "none.jpg":
        current_image_url = url_for("static", filename="images/" + brand_obj.image)
    else:
        current_image_url = None

    if not form.is_submitted():
        form.name.data = brand_obj.name
        form.desc.data = brand_obj.desc
        form.status.data = brand_obj.status

    return render_template(
        "backend/admin/pages/brand/edit.html",
        form=form,
        brand=brand_obj,
        current_image_url=current_image_url,
        os=os
    )


# ============================================================
# Delete brand
# ============================================================

@brand_bp.route("/admin/brand/delete/<int:brand_id>", methods=["POST"])
def brand_delete(brand_id):
    brand_obj = Brand.query.get_or_404(brand_id)

    used_by_product = Product.query.filter_by(brand_id=brand_obj.id).first()

    if used_by_product:
        flash("Cannot delete this brand because some products are using it.", "error")
        return redirect(url_for("brand.brand"))

    try:
        delete_brand_image(brand_obj.image)

        db.session.delete(brand_obj)
        db.session.commit()

        flash("Brand Deleted Successfully", "success")

    except Exception as e:
        db.session.rollback()
        print("Brand Delete Error:", e)
        flash("Error deleting brand.", "error")

    return redirect(url_for("brand.brand"))