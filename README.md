# Facturation Simple

Application web locale (Flask + SQLite) pour créer des factures PDF : gestion des clients, numérotation automatique des factures, lignes de service/produit en MGA/USD/EUR avec taux de change, signature par image transparente.

## Installation (Ubuntu)

WeasyPrint (génération des PDF) a besoin de quelques bibliothèques système :

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip \
  libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
  libgdk-pixbuf2.0-0 libffi-dev
```

## Lancement

```bash
./run.sh
```

Le script crée automatiquement un environnement virtuel Python, installe les dépendances (`requirements.txt`) et démarre le serveur sur **http://127.0.0.1:5000**.

Au premier lancement, ouvrez l'application, allez dans **Paramètres** pour renseigner les informations de votre société, le préfixe de numérotation, et éventuellement uploader votre image de signature (PNG transparent).

## Utilisation

1. **Clients** : créez vos clients (nom, adresse, contact, NIF/STAT).
2. **Factures** : créez une facture, choisissez la date et le client, ajoutez des lignes.
   - Chaque ligne peut être en MGA, USD ou EUR.
   - Si la devise n'est pas MGA, indiquez le taux de change vers MGA : la ligne affichera le prix unitaire dans sa devise d'origine ainsi que le taux appliqué, et son total sera automatiquement converti en MGA.
   - Le total de la facture est toujours affiché en MGA.
3. Le numéro de facture est généré automatiquement au format `PREFIXE/AAAA-0001` (le compteur redémarre chaque année). Vous pouvez le modifier manuellement si besoin.
4. Cliquez sur **PDF** pour télécharger la facture.

## Sauvegarde de la base de données

La base SQLite se trouve dans `instance/app.db`. Deux façons de la sauvegarder :

- Depuis l'application : **Paramètres → Télécharger la sauvegarde** (télécharge une copie horodatée).
- Manuellement : copiez simplement le fichier `instance/app.db` (et le dossier `instance/uploads/` pour la signature) vers un support de sauvegarde.

## Structure du projet

```
app/
├── models.py            # Client, Invoice, InvoiceLine, Settings
├── routes/               # clients, invoices, settings
├── pdf.py                # génération PDF (WeasyPrint)
├── templates/             # pages HTML + template d'impression
└── static/css/            # style
instance/
├── app.db                # base SQLite (créée automatiquement)
└── uploads/                # image de signature
```
