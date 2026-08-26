import os
from datetime import datetime

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

from app import db
from app.models import get_settings

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

ALLOWED_SIGNATURE_EXT = {"png"}


@settings_bp.route("/", methods=["GET", "POST"])
def edit_settings():
    settings = get_settings()

    if request.method == "POST":
        settings.nom_societe = request.form.get("nom_societe", "").strip()
        settings.adresse = request.form.get("adresse", "").strip()
        settings.telephone = request.form.get("telephone", "").strip()
        settings.email = request.form.get("email", "").strip()
        settings.nif = request.form.get("nif", "").strip()
        settings.stat = request.form.get("stat", "").strip()
        settings.identifiant = request.form.get("identifiant", "").strip()
        settings.prefixe_facture = request.form.get("prefixe_facture", "FACT").strip() or "FACT"
        settings.prefixe_proforma = (
            request.form.get("prefixe_proforma", "PROFORMA").strip() or "PROFORMA"
        )

        signature = request.files.get("signature")
        if signature and signature.filename:
            ext = signature.filename.rsplit(".", 1)[-1].lower()
            if ext not in ALLOWED_SIGNATURE_EXT:
                flash("La signature doit être une image PNG.", "error")
                return render_template("settings.html", settings=settings)
            filename = secure_filename("signature.png")
            signature.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            settings.signature_filename = filename

        db.session.commit()
        flash("Paramètres enregistrés.", "success")
        return redirect(url_for("settings.edit_settings"))

    return render_template("settings.html", settings=settings)


@settings_bp.route("/signature")
def signature_image():
    settings = get_settings()
    if not settings.signature_filename:
        abort(404)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"], settings.signature_filename
    )


@settings_bp.route("/backup")
def backup_db():
    db_path = os.path.join(current_app.instance_path, "app.db")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    return send_file(
        db_path, as_attachment=True, download_name=f"backup-{timestamp}.db"
    )
