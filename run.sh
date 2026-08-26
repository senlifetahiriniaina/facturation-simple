#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d venv ]; then
  echo "Création de l'environnement virtuel..."
  python3 -m venv venv
fi

source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

export FLASK_APP=app:create_app
export FLASK_RUN_HOST=127.0.0.1
export FLASK_RUN_PORT=5000

echo "Application disponible sur http://127.0.0.1:5000"
flask run
