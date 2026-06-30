from flask import Blueprint, render_template, redirect, flash, url_for
from extensions import db
from form.VoucherForm import VoucherForm
from models import Voucher

voucher_bp = Blueprint('voucher', __name__)

@voucher_bp.route('/admin/voucher')
def admin_voucher():
    vouchers = Voucher.query.all()
    return render_template('backend/admin/pages/voucher/voucher.html', vouchers=vouchers)


@voucher_bp.route('/admin/voucher/add', methods=['GET', 'POST'])
def admin_voucher_add():
    form = VoucherForm()
    if form.validate_on_submit():
        code_upper = form.code.data.strip().upper()
        existing = Voucher.query.filter_by(code=code_upper).first()
        if existing:
            flash('Voucher code already exists!', 'danger')
            return render_template('backend/admin/pages/voucher/add.html', form=form)

        min_spend_val = float(form.min_spend.data) if form.min_spend.data is not None else 0.0
        usage_limit_val = int(form.usage_limit.data) if form.usage_limit.data is not None else None

        voucher = Voucher(
            code=code_upper,
            min_spend=min_spend_val,
            usage_limit=usage_limit_val,
            usage_count=0,
            status=form.status.data
        )
        db.session.add(voucher)
        db.session.commit()
        
        flash('Voucher has been added successfully!', 'success')
        return redirect(url_for('voucher.admin_voucher'))

    return render_template('backend/admin/pages/voucher/add.html', form=form)


@voucher_bp.route('/admin/voucher/edit/<int:voucher_id>', methods=['GET', 'POST'])
def admin_voucher_edit(voucher_id):
    form = VoucherForm()
    voucher = Voucher.query.get_or_404(voucher_id)
    
    if form.validate_on_submit():
        code_upper = form.code.data.strip().upper()
        existing = Voucher.query.filter(
            Voucher.code == code_upper,
            Voucher.id != voucher.id
        ).first()
        if existing:
            flash('Voucher code already exists!', 'danger')
            return render_template('backend/admin/pages/voucher/edit.html', voucher=voucher, form=form)

        min_spend_val = float(form.min_spend.data) if form.min_spend.data is not None else 0.0
        usage_limit_val = int(form.usage_limit.data) if form.usage_limit.data is not None else None
        usage_count_val = int(form.usage_count.data) if form.usage_count.data is not None else 0

        voucher.code = code_upper
        voucher.min_spend = min_spend_val
        voucher.usage_limit = usage_limit_val
        voucher.usage_count = usage_count_val
        voucher.status = form.status.data
        
        db.session.commit()
        flash('Voucher has been updated successfully!', 'success')
        return redirect(url_for('voucher.admin_voucher'))
            
    if not form.is_submitted():
        form.code.data = voucher.code
        form.min_spend.data = voucher.min_spend
        form.usage_limit.data = voucher.usage_limit
        form.usage_count.data = voucher.usage_count
        form.status.data = voucher.status
        
    return render_template('backend/admin/pages/voucher/edit.html', voucher=voucher, form=form)


@voucher_bp.route('/admin/voucher/delete/<int:voucher_id>', methods=['POST'])
def admin_voucher_delete(voucher_id):
    try:
        voucher = Voucher.query.get_or_404(voucher_id)
        db.session.delete(voucher)
        db.session.commit()
        
        flash('Voucher has been deleted successfully!', 'success')
        return redirect(url_for('voucher.admin_voucher'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting voucher: {e}")
        flash('Error deleting voucher', 'danger')
        return redirect(url_for('voucher.admin_voucher'))
