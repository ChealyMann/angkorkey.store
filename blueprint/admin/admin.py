from flask import Blueprint, render_template, redirect, url_for, request, flash
from models.Setting import Setting
from extensions import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def _admin():
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/dashboard')
def admin():
    return redirect(url_for('product.product'))

@admin_bp.route('/admin/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        telegram_username = request.form.get('telegram_username', '').strip()
        facebook_url = request.form.get('facebook_url', '').strip()
        tiktok_url = request.form.get('tiktok_url', '').strip()
        phone1 = request.form.get('phone1', '').strip()
        phone2 = request.form.get('phone2', '').strip()

        if telegram_username.startswith('@'):
            telegram_username = telegram_username[1:]

        Setting.set_val('telegram_username', telegram_username)
        Setting.set_val('facebook_url', facebook_url)
        Setting.set_val('tiktok_url', tiktok_url)
        Setting.set_val('phone1', phone1)
        Setting.set_val('phone2', phone2)

        flash("Settings updated successfully.", "success")
        return redirect(url_for('admin.settings'))

    return render_template('backend/admin/pages/settings.html',
        telegram_username=Setting.get_val('telegram_username', 'Angkorkey_Store'),
        facebook_url=Setting.get_val('facebook_url', ''),
        tiktok_url=Setting.get_val('tiktok_url', ''),
        phone1=Setting.get_val('phone1', ''),
        phone2=Setting.get_val('phone2', ''),
    )
