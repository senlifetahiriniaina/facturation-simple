from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.models import Client

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")


@clients_bp.route("/")
def list_clients():
    clients = Client.query.order_by(Client.nom).all()
    return render_template("clients/list.html", clients=clients)


@clients_bp.route("/new", methods=["GET", "POST"])
def new_client():
    if request.method == "POST":
        client = Client(
            nom=request.form["nom"].strip(),
            adresse=request.form.get("adresse", "").strip(),
            telephone=request.form.get("telephone", "").strip(),
            email=request.form.get("email", "").strip(),
            nif=request.form.get("nif", "").strip(),
            stat=request.form.get("stat", "").strip(),
        )
        db.session.add(client)
        db.session.commit()
        flash("Client créé.", "success")
        return redirect(url_for("clients.list_clients"))
    return render_template("clients/form.html", client=None)


@clients_bp.route("/<int:client_id>/edit", methods=["GET", "POST"])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == "POST":
        client.nom = request.form["nom"].strip()
        client.adresse = request.form.get("adresse", "").strip()
        client.telephone = request.form.get("telephone", "").strip()
        client.email = request.form.get("email", "").strip()
        client.nif = request.form.get("nif", "").strip()
        client.stat = request.form.get("stat", "").strip()
        db.session.commit()
        flash("Client mis à jour.", "success")
        return redirect(url_for("clients.list_clients"))
    return render_template("clients/form.html", client=client)


@clients_bp.route("/<int:client_id>/delete", methods=["POST"])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    if client.invoices:
        flash(
            "Impossible de supprimer ce client : des factures lui sont associées.",
            "error",
        )
        return redirect(url_for("clients.list_clients"))
    db.session.delete(client)
    db.session.commit()
    flash("Client supprimé.", "success")
    return redirect(url_for("clients.list_clients"))
