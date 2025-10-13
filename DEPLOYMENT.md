# Déploiement Docker — ANNOOR (annoor.com)

Déploiement “prod-ready” d’un site Django sur un **VPS OVH** avec **Docker Compose** :
**Caddy** (HTTPS auto Let’s Encrypt) + **Gunicorn** (app Django) + **PostgreSQL** (base).
Volumes persistants pour **static**, **media**, **DB**.

> Stack correspondante aux fichiers fournis : `docker-compose.yml`, `Caddyfile`, `docker/Dockerfile`, `docker/entrypoint.sh`, `docker/gunicorn.conf.py`, `.env.production.example`.

---

## 0) Prérequis

* Un **VPS OVH** (Debian/Ubuntu recommandés) avec accès root/SSH.
* **Docker** et **Docker Compose plugin**.
* Un **domaine** pointant vers l’IP publique du VPS :

  * `annoor.com` → IP du VPS (A record)
  * `www.annoor.com` → IP du VPS (A record)
* Ports **80** et **443** ouverts (pare-feu OVH + UFW/NFTables sur le VPS).

### Installer Docker & Compose

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# Docker repository
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo $ID)/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/$(. /etc/os-release; echo $ID) \
  $(. /etc/os-release; echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# (Optionnel) exécuter docker sans sudo
sudo usermod -aG docker $USER
# Déconnecte/reconnecte ta session SSH pour appliquer le groupe.
```

---

## 1) Récupérer le code et préparer l’environnement

```bash
# Cloner le repo (ou pull si déjà présent)
git clone https://github.com/<TON_ORG>/<TON_REPO>.git annoorsite
cd annoorsite
```

Créer le fichier d’environnement :

```bash
cp .env.production.example .env
nano .env
```

**À adapter** dans `.env` :

```env
SECRET_KEY=remplace-par-une-valeur-secrète-longue
DEBUG=False
ALLOWED_HOSTS=annoor.com,www.annoor.com
CSRF_TRUSTED_ORIGINS=https://annoor.com,https://www.annoor.com

DB_ENGINE=postgres
DB_NAME=annoor
DB_USER=annoor
DB_PASSWORD=mot-de-passe-tres-fort
DB_HOST=db
DB_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@annoor.com

# Gunicorn (optionnel)
GUNICORN_WORKERS=3
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=30
GUNICORN_LOGLEVEL=info
```

> **Important** : `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` doivent contenir les domaines finaux en **HTTPS** (pour CSRF).

---

## 2) Lancer la stack

> Assure-toi que les enregistrements DNS sont déjà propagés vers l’IP du VPS.

```bash
# Build & run (en tâche de fond)
docker compose up -d --build
```

La première mise en route va :

* Construire l’image de l’app,
* Démarrer Postgres,
* Exécuter `migrate` et `collectstatic` (via `docker/entrypoint.sh`),
* Servir Django sur `web:8000`,
* Exposer Caddy sur **80/443** avec HTTPS automatique pour `annoor.com`.

Créer un superutilisateur :

```bash
docker compose exec web python manage.py createsuperuser
```

---

## 3) Structure des services

* **web** : Django + Gunicorn (port interne 8000)
* **db** : PostgreSQL 16 (volume `pg_data`)
* **caddy** : reverse-proxy + TLS (ports 80/443)

Volumes :

* `pg_data` → données PostgreSQL
* `static_data` → `/vol/static` (fichiers collectés Django)
* `media_data` → `/vol/media` (uploads CKEditor, etc.)
* `caddy_data`, `caddy_config` → certificats Let’s Encrypt et confs Caddy

---

## 4) Commandes utiles

### Logs temps réel

```bash
docker compose logs -f
# ou par service :
docker compose logs -f web
docker compose logs -f caddy
docker compose logs -f db
```

### Redémarrer / recharger

```bash
docker compose restart web
docker compose restart caddy
```

### Mise à jour (rolling update simple)

```bash
git pull origin main
docker compose up -d --build
```

> Caddy reste up; `web` est reconstruit puis redéployé, migrations & collectstatic sont relancés automatiquement par l’entrypoint.

---

## 5) Sauvegardes & restauration

### Sauvegarde base PostgreSQL

```bash
# Dump SQL dans un fichier local
docker compose exec -T db pg_dump -U "$DB_USER" "$DB_NAME" > backup_$(date +%F).sql
```

Restauration :

```bash
cat backup_YYYY-MM-DD.sql | docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME"
```

### Sauvegarde uploads (media)

Les fichiers sont dans le **volume** `media_data`. Deux approches :

* **Archive depuis le conteneur caddy** (monté en lecture seule) :

  ```bash
  docker compose exec caddy sh -lc 'cd /vol && tar czf - media' > media_backup.tgz
  ```

* **Ou via un bind mount** si tu bascules le volume sur un dossier hôte.

---

## 6) Email en production

Remplacer l’email backend **console** par un SMTP réel (Postmark, Mailgun, OVH, etc.).
Exemple variables supplémentaires dans `.env` :

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailprovider.com
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@annoor.com
EMAIL_HOST_PASSWORD=mot-de-passe
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=contact@annoor.com
```

---

## 7) Médiamap (CKEditor / uploads)

* Les images envoyées via CKEditor vont sous `MEDIA_ROOT` → monté en `/vol/media`.
* Servies directement par **Caddy** sur `/media/*` (cf. `Caddyfile`).

---

## 8) Sécurité & durcissement

* **`DEBUG=False`** en production.
* **Mots de passe** forts pour Postgres & superuser Django.
* **Pare-feu** : n’ouvrir que **80** et **443** (Caddy).
  (Ports internes Docker ne sont pas exposés publiquement.)
* **Mises à jour** : appliquer `apt upgrade` régulièrement sur le VPS + rebuild images.

Optional (fortement recommandé) :

* Activer **UFW** :

  ```bash
  sudo ufw allow OpenSSH
  sudo ufw allow 80
  sudo ufw allow 443
  sudo ufw enable
  ```
* **Backups** réguliers DB + media (cron/Ansible).

---

## 9) Dépannage

* **Le HTTPS ne s’installe pas** :

  * Vérifie les **DNS** vers l’IP du VPS.
  * Regarde `docker compose logs -f caddy`.
  * Temporise le temps de propagation DNS.

* **Erreur 502 / Bad Gateway** :

  * `web` est-il UP ? `docker compose ps`
  * Logs `web` pour erreurs Python/Migrations.

* **Statique/Media absents** :

  * Vérifie que `collectstatic` est bien exécuté (logs `web`).
  * Vérifie les volumes montés dans `caddy` (lecture seule OK).

* **CSRF** :

  * Vérifie `CSRF_TRUSTED_ORIGINS` (https, domaines exacts).

---

## 10) Rollback rapide

Si un build récent pose souci :

```bash
# Revenir au commit stable
git checkout <commit_stable>
docker compose up -d --build
```

Sinon, pull l’image précédente si tu pousses sur un registry.

---

## 11) Déploiement staging (facultatif)

Tu peux dupliquer la stack avec un autre **fichier compose** (ex. `docker-compose.staging.yml`) et un autre domaine (ex. `staging.annoor.com`) :

* Nouveau `Caddyfile` ou nouveau **site block**.
* `.env.staging` avec DB/Creds dédiés.
* Port 443 déjà géré par Caddy pour ce second host.

---

## 12) Checklist avant go-live

* [ ] DNS `annoor.com` et `www.annoor.com` pointent vers le VPS.
* [ ] `.env` finalisé (`SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, SMTP si besoin).
* [ ] `docker compose up -d --build` OK.
* [ ] `createsuperuser` créé.
* [ ] Test routes : `/admin/`, `/`, `/services/`, `/projects/`, `/blog/`, `/contact/`.
* [ ] Upload image via CKEditor et affichage.
* [ ] Sauvegarde DB testée (`pg_dump`).
* [ ] UFW actif (80/443/SSH).
* [ ] HTTPS émis par Let’s Encrypt (caddy logs OK).

---

## 13) Commandes “mémo”

```bash
# Build & run
docker compose up -d --build

# Arrêter
docker compose down

# Voir containers
docker compose ps

# Logs
docker compose logs -f
docker compose logs -f web

# Migrations manuelles
docker compose exec web python manage.py migrate

# Collect static (manuel)
docker compose exec web python manage.py collectstatic --noinput

# Shell Django
docker compose exec web python manage.py shell
```