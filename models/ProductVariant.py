import enum
from extensions import db


class StockStatus(enum.Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


class VariantType(db.Model):
    __tablename__ = "variant_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)

    options = db.relationship(
        "VariantOption",
        back_populates="variant_type",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<VariantType {self.name}>"


class VariantOption(db.Model):
    __tablename__ = "variant_option"

    id = db.Column(db.Integer, primary_key=True)

    variant_type_id = db.Column(
        db.Integer,
        db.ForeignKey("variant_type.id"),
        nullable=False,
        index=True
    )

    value = db.Column(db.String(80), nullable=False)

    # For color, meta can be "#000000"
    # For type/size, meta can be empty
    meta = db.Column(db.String(120), nullable=True)

    variant_type = db.relationship(
        "VariantType",
        back_populates="options"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "variant_type_id",
            "value",
            name="uq_variant_option_type_value"
        ),
    )

    def __repr__(self):
        return f"<VariantOption {self.value}>"


class ProductOptionType(db.Model):
    """
    This controls which option groups a product uses.

    Example:
    QKZ AK3 uses Color + Type.
    Monitor Stand uses Color + Size.
    """

    __tablename__ = "product_option_type"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False,
        index=True
    )

    variant_type_id = db.Column(
        db.Integer,
        db.ForeignKey("variant_type.id"),
        nullable=False,
        index=True
    )

    sort_order = db.Column(db.Integer, nullable=False, default=0)

    product = db.relationship("Product", back_populates="option_types")
    variant_type = db.relationship("VariantType")

    __table_args__ = (
        db.UniqueConstraint(
            "product_id",
            "variant_type_id",
            name="uq_product_option_type"
        ),
    )


class ProductVariant(db.Model):
    __tablename__ = "product_variant"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False,
        index=True
    )

    sku = db.Column(db.String(100), nullable=True, unique=True)

    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    cost = db.Column(db.Float, nullable=True)

    # Updated to Enum
    stock = db.Column(
        db.Enum(StockStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=StockStatus.OUT_OF_STOCK
    )

    status = db.Column(db.String(5), nullable=False, default="true")

    # Example:
    # color:black|type:with-mic
    # color:black|size:large
    option_key = db.Column(db.String(255), nullable=False, index=True)

    product = db.relationship("Product", back_populates="variants")

    selected_options = db.relationship(
        "ProductVariantOption",
        back_populates="variant",
        cascade="all, delete-orphan",
        lazy=True
    )

    images = db.relationship(
        "ProductVariantImage",
        back_populates="variant",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="ProductVariantImage.sort_order"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "product_id",
            "option_key",
            name="uq_product_variant_option_key"
        ),
    )

    # ------------------------------------------------------------
    # Check if this variant has discount
    # Example:
    # old_price = 15
    # price = 10
    # result = True
    # ------------------------------------------------------------
    @property
    def has_discount(self):
        return (
            self.status == "true"
            and self.old_price is not None
            and self.price is not None
            and float(self.old_price) > float(self.price)
        )

    @property
    def main_image(self):
        if self.images:
            return self.images[0].image
        return self.product.image

    def options_dict(self):
        data = {}

        for selected in self.selected_options:
            option = selected.option
            data[option.variant_type.slug] = option.value

        return data

    def __repr__(self):
        stock_value = self.stock.value if hasattr(self.stock, "value") else self.stock
        return f"<ProductVariant product={self.product_id} sku={self.sku} stock={stock_value}>"


class ProductVariantOption(db.Model):
    __tablename__ = "product_variant_option"

    id = db.Column(db.Integer, primary_key=True)

    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variant.id"),
        nullable=False,
        index=True
    )

    variant_option_id = db.Column(
        db.Integer,
        db.ForeignKey("variant_option.id"),
        nullable=False,
        index=True
    )

    variant = db.relationship(
        "ProductVariant",
        back_populates="selected_options"
    )

    option = db.relationship("VariantOption")

    __table_args__ = (
        db.UniqueConstraint(
            "product_variant_id",
            "variant_option_id",
            name="uq_product_variant_option"
        ),
    )


class ProductVariantImage(db.Model):
    __tablename__ = "product_variant_image"

    id = db.Column(db.Integer, primary_key=True)

    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variant.id"),
        nullable=False,
        index=True
    )

    image = db.Column(db.String(120), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    variant = db.relationship(
        "ProductVariant",
        back_populates="images"
    )