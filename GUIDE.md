# Guide d'exploitation

Ce guide explique comment utiliser l'application au quotidien : la lancer, mettre à jour son code, sauvegarder et restaurer vos données. Pour l'installation initiale et le détail des fonctionnalités, voir [`README.md`](README.md).

## 1. Lancer l'application

Depuis le dossier du projet :

```bash
./run.sh
```

Le script installe/actualise automatiquement les dépendances Python (dans un environnement virtuel `venv/`, créé au premier lancement) puis démarre le serveur. Ouvrez ensuite votre navigateur sur :

```
http://127.0.0.1:5000
```

Pour arrêter l'application, retournez dans le terminal où `./run.sh` tourne et appuyez sur `Ctrl+C`.

> Vos données (clients, factures, signature) ne sont **jamais** perdues entre deux lancements : elles vivent dans le dossier `instance/`, indépendant du code de l'application.

## 2. Mettre à jour le code

Quand une nouvelle version de l'application est disponible (nouvelles fonctionnalités, corrections) :

```bash
git pull
./run.sh
```

- `git pull` récupère le nouveau code.
- `./run.sh` réinstalle automatiquement les dépendances si elles ont changé, puis relance le serveur.

Le dossier `instance/` (base de données `app.db` et signature) n'est pas suivi par git — une mise à jour du code ne touche jamais à vos données.

Si vous avez modifié des fichiers du projet vous-même et que `git pull` refuse de continuer (conflit), n'exécutez pas de commande destructive (`git reset --hard`, `git checkout .`, etc.) sans être sûr de ce que vous faites : contactez la personne qui vous a fourni l'application au besoin.

## 3. Sauvegarder la base de données

Toutes vos données (clients, factures) sont dans un seul fichier SQLite : `instance/app.db`. Votre signature est dans `instance/uploads/`.

**Méthode recommandée (depuis l'application) :**
1. Allez dans **Paramètres**.
2. Cliquez sur **Télécharger la sauvegarde**.
3. Un fichier `backup-AAAAMMJJ-HHMM.db` est téléchargé — rangez-le dans un endroit sûr (clé USB, disque externe, cloud personnel...).

**Méthode manuelle (copie de fichiers) :**
```bash
cp instance/app.db ~/sauvegardes/app-$(date +%Y%m%d).db
cp -r instance/uploads ~/sauvegardes/uploads-$(date +%Y%m%d)
```

**Conseil de fréquence :** sauvegardez au moins après chaque session de facturation importante, ou automatisez une copie quotidienne avec une tâche planifiée (`cron`) si vous êtes à l'aise avec ça :
```bash
# Exemple de ligne crontab (crontab -e) : sauvegarde tous les jours à 20h
0 20 * * * cp /chemin/vers/facturation-simple/instance/app.db /chemin/vers/sauvegardes/app-$(date +\%Y\%m\%d).db
```

## 4. Restaurer une sauvegarde

Il n'y a volontairement pas de bouton "Restaurer" dans l'application, pour éviter d'écraser votre base actuelle par erreur en un clic depuis le navigateur. La restauration se fait manuellement, en toute connaissance de cause :

1. **Arrêtez l'application** (`Ctrl+C` dans le terminal où elle tourne).
2. Par précaution, mettez de côté la base actuelle :
   ```bash
   mv instance/app.db instance/app.db.avant-restauration
   ```
3. Copiez votre fichier de sauvegarde à la place :
   ```bash
   cp ~/sauvegardes/backup-20260101-2000.db instance/app.db
   ```
4. Relancez l'application :
   ```bash
   ./run.sh
   ```
5. Vérifiez dans **Factures** et **Clients** que les données restaurées sont bien celles attendues.

Si quelque chose ne va pas, vous pouvez toujours revenir à l'état précédent en restaurant `instance/app.db.avant-restauration`.
