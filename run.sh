#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d venv ]; then
  echo "Création de l'environnement virtuel..."
  python3 -m venv venv
fi

source venv/bin/activate

PIP_NET_OPTS="--retries 5 --timeout 30"

if ! pip install --quiet --upgrade pip $PIP_NET_OPTS; then
  echo "Impossible de contacter PyPI pour mettre à jour pip (problème réseau)." >&2
  echo "Voir la section Dépannage de GUIDE.md." >&2
  exit 1
fi

if ! pip install --quiet -r requirements.txt $PIP_NET_OPTS; then
  echo "Impossible d'installer les dépendances (problème réseau vers PyPI)." >&2
  echo "Voir la section Dépannage de GUIDE.md." >&2
  exit 1
fi

export FLASK_APP=app:create_app
export FLASK_RUN_HOST=127.0.0.1
export FLASK_RUN_PORT=5000

echo "Application disponible sur http://127.0.0.1:5000"
flask run
