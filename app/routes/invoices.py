from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app import db
from app.models import CURRENCIES, INVOICE_TYPES, Client, Invoice, InvoiceLine, get_settings
from app.pdf import render_invoice_pdf

invoices_bp = Blueprint("invoices", __name__, url_prefix="/invoices")


def _to_decimal(value, default="0"):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return Decimal(default)


def _prefix_for_type(settings, type_facture):
    if type_facture == "proforma":
        return settings.prefixe_proforma or "PROFORMA"
    return settings.prefixe_facture or "FACT"


def _parse_type(form):
    type_facture = form.get("type_facture", "facture")
    return type_facture if type_facture in INVOICE_TYPES else "facture"


def _parse_lines(form):
    descriptions = form.getlist("description[]")
    quantites = form.getlist("quantite[]")
    devises = form.getlist("devise[]")
    prix = form.getlist("prix_unitaire[]")
    taux = form.getlist("taux_change[]")

    lines = []
    for i, description in enumerate(descriptions):
        description = description.strip()
        if not description:
            continue
        devise = devises[i] if i < len(devises) else "MGA"
        if devise not in CURRENCIES:
            devise = "MGA"
        taux_value = taux[i] if i < len(taux) else ""
        taux_decimal = _to_decimal(taux_value) if devise != "MGA" and taux_value else None
        lines.append(
            InvoiceLine(
                description=description,
                quantite=_to_decimal(quantites[i] if i < len(quantites) else "1", "1"),
                devise=devise,
                prix_unitaire=_to_decimal(prix[i] if i < len(prix) else "0"),
                taux_change=taux_decimal,
            )
        )
    return lines


@invoices_bp.route("/")
def list_invoices():
    invoices = Invoice.query.order_by(Invoice.date_facture.desc(), Invoice.id.desc()).all()
    return render_template("invoices/list.html", invoices=invoices)


@invoices_bp.route("/new", methods=["GET", "POST"])
def new_invoice():
    clients = Client.query.order_by(Client.nom).all()
    settings = get_settings()

    if request.method == "POST":
        type_facture = _parse_type(request.form)
        client_id = request.form.get("client_id", type=int)
        if not client_id:
            flash("Veuillez sélectionner un client.", "error")
            return render_template(
                "invoices/form.html",
                invoice=None,
                clients=clients,
                currencies=CURRENCIES,
                invoice_types=INVOICE_TYPES,
                today=date.today().isoformat(),
            )

        date_str = request.form.get("date_facture") or date.today().isoformat()
        date_facture = datetime.strptime(date_str, "%Y-%m-%d").date()

        lines = _parse_lines(request.form)
        if not lines:
            flash("Ajoutez au moins une ligne à la facture.", "error")
            return render_template(
                "invoices/form.html",
                invoice=None,
                clients=clients,
                currencies=CURRENCIES,
                invoice_types=INVOICE_TYPES,
                today=date.today().isoformat(),
            )

        numero = request.form.get("numero", "").strip()
        if not numero:
            numero = Invoice.next_numero(_prefix_for_type(settings, type_facture), date_facture.year)

        invoice = Invoice(
            numero=numero,
            type_facture=type_facture,
            date_facture=date_facture,
            client_id=client_id,
            notes=request.form.get("notes", "").strip(),
            lines=lines,
        )
        db.session.add(invoice)
        db.session.commit()
        flash(
            "Proforma créé." if type_facture == "proforma" else "Facture créée.",
            "success",
        )
        return redirect(url_for("invoices.view_invoice", invoice_id=invoice.id))

    year = date.today().year
    suggested_numeros = {
        "facture": Invoice.next_numero(settings.prefixe_facture, year),
        "proforma": Invoice.next_numero(settings.prefixe_proforma, year),
    }
    return render_template(
        "invoices/form.html",
        invoice=None,
        clients=clients,
        currencies=CURRENCIES,
        invoice_types=INVOICE_TYPES,
        suggested_numeros=suggested_numeros,
        today=date.today().isoformat(),
    )


@invoices_bp.route("/<int:invoice_id>")
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    settings = get_settings()
    return render_template("invoices/view.html", invoice=invoice, settings=settings)


@invoices_bp.route("/<int:invoice_id>/edit", methods=["GET", "POST"])
def edit_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    clients = Client.query.order_by(Client.nom).all()

    if request.method == "POST":
        type_facture = _parse_type(request.form)
        client_id = request.form.get("client_id", type=int)
        if not client_id:
            flash("Veuillez sélectionner un client.", "error")
            return render_template(
                "invoices/form.html",
                invoice=invoice,
                clients=clients,
                currencies=CURRENCIES,
                invoice_types=INVOICE_TYPES,
            )

        date_str = request.form.get("date_facture") or date.today().isoformat()
        invoice.date_facture = datetime.strptime(date_str, "%Y-%m-%d").date()

        lines = _parse_lines(request.form)
        if not lines:
            flash("Ajoutez au moins une ligne à la facture.", "error")
            return render_template(
                "invoices/form.html",
                invoice=invoice,
                clients=clients,
                currencies=CURRENCIES,
                invoice_types=INVOICE_TYPES,
            )

        numero = request.form.get("numero", "").strip()
        if numero:
            invoice.numero = numero
        invoice.type_facture = type_facture
        invoice.client_id = client_id
        invoice.notes = request.form.get("notes", "").strip()
        invoice.lines = lines
        db.session.commit()
        flash("Facture mise à jour.", "success")
        return redirect(url_for("invoices.view_invoice", invoice_id=invoice.id))

    settings = get_settings()
    year = date.today().year
    suggested_numeros = {
        "facture": Invoice.next_numero(settings.prefixe_facture, year),
        "proforma": Invoice.next_numero(settings.prefixe_proforma, year),
    }
    return render_template(
        "invoices/form.html",
        invoice=invoice,
        clients=clients,
        currencies=CURRENCIES,
        invoice_types=INVOICE_TYPES,
        suggested_numeros=suggested_numeros,
    )


@invoices_bp.route("/<int:invoice_id>/delete", methods=["POST"])
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    db.session.delete(invoice)
    db.session.commit()
    flash("Facture supprimée.", "success")
    return redirect(url_for("invoices.list_invoices"))


@invoices_bp.route("/<int:invoice_id>/pdf")
def invoice_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    settings = get_settings()
    pdf_bytes = render_invoice_pdf(invoice, settings)
    filename = invoice.numero.replace("/", "-") + ".pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
