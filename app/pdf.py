import os

from flask import current_app, render_template
from weasyprint import HTML


def render_invoice_pdf(invoice, settings):
    signature_path = None
    if settings.signature_filename:
        candidate = os.path.join(current_app.config["UPLOAD_FOLDER"], settings.signature_filename)
        if os.path.exists(candidate):
            signature_path = candidate

    html_content = render_template(
        "invoice_pdf.html",
        invoice=invoice,
        settings=settings,
        signature_path=signature_path,
    )
    return HTML(string=html_content, base_url=current_app.root_path).write_pdf()
