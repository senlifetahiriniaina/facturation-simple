from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.models import CURRENCIES, Product

products_bp = Blueprint("products", __name__, url_prefix="/products")


def _to_decimal(value, default="0"):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return Decimal(default)


@products_bp.route("/")
def list_products():
    products = Product.query.order_by(Product.nom).all()
    return render_template("products/list.html", products=products)


@products_bp.route("/new", methods=["GET", "POST"])
def new_product():
    if request.method == "POST":
        devise = request.form.get("devise", "MGA")
        if devise not in CURRENCIES:
            devise = "MGA"
        product = Product(
            nom=request.form["nom"].strip(),
            description=request.form.get("description", "").strip(),
            devise=devise,
            prix_unitaire=_to_decimal(request.form.get("prix_unitaire", "0")),
        )
        db.session.add(product)
        db.session.commit()
        flash("Produit créé.", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/form.html", product=None, currencies=CURRENCIES)


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        devise = request.form.get("devise", "MGA")
        if devise not in CURRENCIES:
            devise = "MGA"
        product.nom = request.form["nom"].strip()
        product.description = request.form.get("description", "").strip()
        product.devise = devise
        product.prix_unitaire = _to_decimal(request.form.get("prix_unitaire", "0"))
        db.session.commit()
        flash("Produit mis à jour.", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/form.html", product=product, currencies=CURRENCIES)


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Produit supprimé.", "success")
    return redirect(url_for("products.list_products"))
