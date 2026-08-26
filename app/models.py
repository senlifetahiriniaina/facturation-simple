from datetime import date, datetime
from decimal import Decimal

from app import db

CURRENCIES = ["MGA", "USD", "EUR"]
INVOICE_TYPES = ["facture", "proforma"]


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    adresse = db.Column(db.String(300))
    telephone = db.Column(db.String(50))
    email = db.Column(db.String(150))
    nif = db.Column(db.String(50))
    stat = db.Column(db.String(50))

    invoices = db.relationship(
        "Invoice", back_populates="client", cascade="all, delete-orphan"
    )


class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    nom_societe = db.Column(db.String(200), default="")
    adresse = db.Column(db.String(300), default="")
    telephone = db.Column(db.String(50), default="")
    email = db.Column(db.String(150), default="")
    nif = db.Column(db.String(50), default="")
    stat = db.Column(db.String(50), default="")
    identifiant = db.Column(db.String(100), default="")
    prefixe_facture = db.Column(db.String(20), default="FACT")
    prefixe_proforma = db.Column(db.String(20), default="PROFORMA")
    signature_filename = db.Column(db.String(200))


def get_settings():
    settings = Settings.query.first()
    if settings is None:
        settings = Settings(prefixe_facture="FACT", prefixe_proforma="PROFORMA")
        db.session.add(settings)
        db.session.commit()
    return settings


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    type_facture = db.Column(db.String(10), nullable=False, default="facture")
    date_facture = db.Column(db.Date, nullable=False, default=date.today)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship("Client", back_populates="invoices")
    lines = db.relationship(
        "InvoiceLine",
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="InvoiceLine.id",
    )

    @property
    def total_mga(self):
        return sum((line.total_mga for line in self.lines), Decimal("0"))

    @staticmethod
    def next_numero(prefixe, annee):
        count = Invoice.query.filter(
            Invoice.numero.like(f"{prefixe}/{annee}-%")
        ).count()
        return f"{prefixe}/{annee}-{count + 1:04d}"


class InvoiceLine(db.Model):
    __tablename__ = "invoice_lines"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    quantite = db.Column(db.Numeric(12, 2), nullable=False, default=1)
    devise = db.Column(db.String(3), nullable=False, default="MGA")
    prix_unitaire = db.Column(db.Numeric(16, 2), nullable=False, default=0)
    taux_change = db.Column(db.Numeric(16, 4))

    invoice = db.relationship("Invoice", back_populates="lines")

    @property
    def total_devise(self):
        return self.quantite * self.prix_unitaire

    @property
    def total_mga(self):
        if self.devise == "MGA":
            return self.total_devise
        return self.total_devise * (self.taux_change or Decimal("0"))
