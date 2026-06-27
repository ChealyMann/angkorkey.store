from flask import request
from flask_paginate import get_page_parameter, Pagination
from sqlalchemy import text

from extensions import db


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False, index=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.id"),
        nullable=False,
        index=True
    )

    brand_id = db.Column(
        db.Integer,
        db.ForeignKey("brand.id", name="fk_product_brand_id_brand"),
        nullable=True,
        index=True
    )

    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    cost = db.Column(db.Float, nullable=True)

    image = db.Column(db.String(100), nullable=True)
    desc = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(5), nullable=False)
    best_selling = db.Column(db.Boolean, default=False, nullable=False)

    images = db.relationship(
        "ProductImage",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    category_name = db.relationship(
        "Category",
        backref="product",
        lazy=True
    )

    brand = db.relationship(
        "Brand",
        backref="products",
        lazy=True
    )

    option_types = db.relationship(
        "ProductOptionType",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True
    )

    variants = db.relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"Product {self.name}"

    # ------------------------------------------------------------
    # ACTIVE VARIANTS
    # Only variants with status == "true"
    # ------------------------------------------------------------
    @property
    def active_variants(self):
        return [
            variant for variant in self.variants
            if variant.status == "true"
        ]

    # ------------------------------------------------------------
    # CHECK IF PRODUCT HAS ACTIVE VARIANTS
    # ------------------------------------------------------------
    @property
    def has_variants(self):
        return len(self.active_variants) > 0

    # ------------------------------------------------------------
    # NORMAL MIN PRICE
    # If product has variants, use lowest active variant price.
    # If no variants, use normal product price.
    # ------------------------------------------------------------
    @property
    def min_price(self):
        if self.has_variants:
            return min(variant.price for variant in self.active_variants)

        return self.price

    # ------------------------------------------------------------
    # NORMAL MAX PRICE
    # If product has variants, use highest active variant price.
    # If no variants, use normal product price.
    # ------------------------------------------------------------
    @property
    def max_price(self):
        if self.has_variants:
            return max(variant.price for variant in self.active_variants)

        return self.price

    # ------------------------------------------------------------
    # NORMAL PRICE TEXT
    # Example:
    # $10.00
    # or
    # $10.00 - $15.00
    # ------------------------------------------------------------
    @property
    def price_text(self):
        if self.has_variants and self.min_price != self.max_price:
            return f"${self.min_price:.2f} - ${self.max_price:.2f}"

        return f"${self.min_price:.2f}"

    # ------------------------------------------------------------
    # NORMAL PRODUCT DISCOUNT
    # This checks discount directly on product table.
    #
    # Example:
    # product.old_price = 20
    # product.price = 15
    # result = True
    # ------------------------------------------------------------
    @property
    def has_product_discount(self):
        return (
            self.old_price is not None
            and self.price is not None
            and float(self.old_price) > float(self.price)
        )

    # ------------------------------------------------------------
    # DISCOUNTED VARIANTS ONLY
    # This returns only active variants that have real discount.
    #
    # Example:
    # Variant Black: old_price 20, price 15 => included
    # Variant White: old_price 20, price 20 => not included
    # ------------------------------------------------------------
    @property
    def discounted_variants(self):
        return [
            variant for variant in self.active_variants
            if variant.old_price is not None
            and variant.price is not None
            and float(variant.old_price) > float(variant.price)
        ]

    # ------------------------------------------------------------
    # CHECK IF ANY VARIANT HAS DISCOUNT
    # ------------------------------------------------------------
    @property
    def has_variant_discount(self):
        return len(self.discounted_variants) > 0

    # ------------------------------------------------------------
    # FINAL DISCOUNT CHECK
    # Used by product card and promotion page display.
    #
    # True if:
    # 1. Product itself has discount
    # OR
    # 2. At least one variant has discount
    # ------------------------------------------------------------
    @property
    def has_discount(self):
        return self.has_product_discount or self.has_variant_discount

    # ------------------------------------------------------------
    # PROMOTION MIN PRICE
    # If variants have discount, use only discounted variant prices.
    # If no discounted variants, use product price.
    # ------------------------------------------------------------
    @property
    def promotion_min_price(self):
        if self.discounted_variants:
            return min(variant.price for variant in self.discounted_variants)

        return self.price

    # ------------------------------------------------------------
    # PROMOTION MAX PRICE
    # ------------------------------------------------------------
    @property
    def promotion_max_price(self):
        if self.discounted_variants:
            return max(variant.price for variant in self.discounted_variants)

        return self.price

    # ------------------------------------------------------------
    # PROMOTION MIN OLD PRICE
    # If variants have discount, use old prices from discounted variants.
    # ------------------------------------------------------------
    @property
    def promotion_min_old_price(self):
        if self.discounted_variants:
            return min(variant.old_price for variant in self.discounted_variants)

        return self.old_price

    # ------------------------------------------------------------
    # PROMOTION MAX OLD PRICE
    # ------------------------------------------------------------
    @property
    def promotion_max_old_price(self):
        if self.discounted_variants:
            return max(variant.old_price for variant in self.discounted_variants)

        return self.old_price

    # ------------------------------------------------------------
    # PROMOTION PRICE TEXT
    # Used when product is on promotion.
    #
    # Example:
    # $10.00
    # or
    # $10.00 - $15.00
    # ------------------------------------------------------------
    @property
    def promotion_price_text(self):
        if self.discounted_variants:
            min_price = self.promotion_min_price
            max_price = self.promotion_max_price

            if min_price != max_price:
                return f"${min_price:.2f} - ${max_price:.2f}"

            return f"${min_price:.2f}"

        return f"${self.price:.2f}"

    # ------------------------------------------------------------
    # PROMOTION OLD PRICE TEXT
    # Used for line-through old price.
    #
    # Example:
    # $20.00
    # or
    # $20.00 - $25.00
    # ------------------------------------------------------------
    @property
    def promotion_old_price_text(self):
        if self.discounted_variants:
            min_old_price = self.promotion_min_old_price
            max_old_price = self.promotion_max_old_price

            if min_old_price != max_old_price:
                return f"${min_old_price:.2f} - ${max_old_price:.2f}"

            return f"${min_old_price:.2f}"

        if self.old_price:
            return f"${self.old_price:.2f}"

        return ""


def getAllProduct():
    page = request.args.get(get_page_parameter(), default=1, type=int)
    per_page = 6
    offset_value = (page - 1) * per_page

    sql = text("""
        SELECT
            p.*,
            c.name AS category_name,
            b.name AS brand_name
        FROM product p
        INNER JOIN category c ON c.id = p.category_id
        LEFT JOIN brand b ON b.id = p.brand_id
        ORDER BY p.id DESC
        LIMIT :limit OFFSET :offset
    """)

    results = db.session.execute(
        sql,
        {
            "limit": per_page,
            "offset": offset_value
        }
    ).fetchall()

    rows = text("""
        SELECT COUNT(*)
        FROM product
    """)

    total_rows = db.session.execute(rows).fetchone()[0]

    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=total_rows,
        css_framework="bootstrap5"
    )

    return {
        "list": results,
        "pagination": pagination,
    }