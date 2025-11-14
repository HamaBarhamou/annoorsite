# ANNOOR — Site vitrine (Django)

Un site vitrine professionnel pour présenter **services**, **références/projets**, **partenaires**, **actualités (blog)** et **contact**.
L’objectif : une base Django élégante, rapide à mettre en route, **SEO-friendly** et facile à éditer via l’admin.

---

## ✨ Fonctionnalités

* **Accueil** avec hero illustré, statistiques, services, projets, logos partenaires et CTA.
* **Services** (liste + page détail avec slug).
* **Références/Projets** (liste filtrable + page détail, galerie d’images).
* **Partenaires** (logo + lien).
* **Blog** (liste filtrable + article détail, **éditeur riche** avec upload d’images).
* **Contact** (formulaire + messages flash + honeypot simple).
* **Contact global** via modèle `SiteContact` (adresse, email, téléphone, réseaux… accessible partout).
* **SEO** : balises méta, OpenGraph/Twitter, JSON-LD, **sitemap.xml**.
* **Admin Django** **personnalisé** (header/pied, page de login brandée).
* **Médias** : gérés localement (Pillow) + CKEditor Uploader.

---

## 🛠️ Pile technique

* **Django 5**
* **SQLite** (dev) — configurable pour Postgres/MySQL.
* **Tailwind** via **CDN** (dev/POC) pour la vitesse d’itération.
* **Pillow** (images), **django-ckeditor** (+ uploader intégré).
* **django.contrib.sitemaps** (sitemaps SEO).

---

## 🚀 Démarrage rapide

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

Ouvre [http://127.0.0.1:8000/](http://127.0.0.1:8000/) et l’admin sur [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## ⚙️ Configuration utile (dev)

Dans `config/settings.py` :

* Médias :

  ```python
  MEDIA_URL = "/media/"
  MEDIA_ROOT = BASE_DIR / "media"
  ```
* Statics (CDN Tailwind, mais dossier présent pour nos fichiers) :

  ```python
  STATIC_URL = "/static/"
  STATICFILES_DIRS = [BASE_DIR / "static"]
  ```
* CKEditor :

  ```python
  CKEDITOR_UPLOAD_PATH = "uploads/"
  CKEDITOR_IMAGE_BACKEND = "pillow"
  ```

> En dev, les URLs media sont servies automatiquement (voir `config/urls.py`).

---

## 🧭 Navigation & URLs

* Accueil : `/`
* Services : `/services/` et `/services/<slug>/`
* Projets : `/projects/` et `/projects/<slug>/`
* Partenaires : `/partners/`
* Blog : `/blog/` et `/blog/<slug>/`
* Contact : `/contact/`
* Admin : `/admin/`
* CKEditor Uploader : `/ckeditor/`
* Sitemap : `/sitemap.xml`

---

## 🧑‍💼 Administration & contenu

Après connexion à l’admin :

1. **SiteContact** : crée/édite **une** entrée (adresse, email, téléphone, réseaux, lien WhatsApp, map…).
2. **Services** : titre, slug auto, résumé (excerpt), body, cover.
3. **Projets** : titre, slug, client, lieu, année, contexte, solution, résultats, cover + **galerie** (images liées).
4. **Partenaires** : nom, site, logo.
5. **Blog / Post** :

   * Titre, slug auto, **Body (éditeur riche CKEditor)**, image **cover** optionnelle.
   * **Insérer une image dans le contenu** :

     * Cliquez l’icône **“Insérer une image”** (petite montagne) dans la barre d’outils.
     * Onglet **“Upload”** → **Parcourir** → **Envoyer au serveur** → **OK**.
     * (⚠️ **Ne pas** utiliser “insérer lien” pour une image locale.)

---

## 📝 Modèles principaux

* `Service(title, slug, excerpt, body, cover)`
* `Project(title, slug, client, location, year, context, solution, results, cover)`

  * `ProjectImage(project, image, caption)`
* `Partner(name, website, logo)`
* `Post(title, slug, body[RichText/CKEditor], published, pub_date, cover)`
* `HomeSettings` (hero + stats) — pour l’Accueil
* `SiteContact(company_name, address, email, phone, socials, whatsapp_url, map_embed_url, …)`

---

## 🔎 SEO & Accessibilité

* **Balises méta** par page (title/description).
* **OpenGraph / Twitter Cards** sur blog et projets.
* **JSON-LD** (ItemList, BlogPosting, Project, AboutPage…).
* **Sitemap** auto : services, projets, posts, pages statiques.
* Fil d’Ariane HTML simple.
* Classes utilitaires Tailwind pour le contraste et le focus.

---

## 🧪 Commandes utiles

```bash
# Créer migrations / migrer
python manage.py makemigrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser

# Collecte des statics (prod)
python manage.py collectstatic --noinput
```

---

## 🧯 Déploiement (checklist rapide)

* `DEBUG = False`
* `ALLOWED_HOSTS = ["example.com", "www.example.com"]`
* `SECRET_KEY` via variable d’environnement.
* `STATIC_ROOT` défini et `collectstatic` exécuté.
* `MEDIA_ROOT` persistant (volume).
* Reverse proxy (Nginx/Caddy) + **Gunicorn**/**Uvicorn**.
* Certificat TLS (Let’s Encrypt).
* Logs & supervision (ex. journald, Sentry…).

Exemple minimal pour `STATIC_ROOT` :

```python
STATIC_ROOT = BASE_DIR / "staticfiles"
```

---

## 🗺️ Structure du projet

```
config/               # settings, urls, wsgi
sitecontent/          # app principale: modèles, vues, admin, sitemaps
templates/            # base.html + pages (home, services, projects, blog, contact, admin override)
templates/admin/      # brand de l'admin (base_site, login)
templates/partials/   # header, footer
static/               # CSS brand admin (static/admin/brand.css), assets
media/                # fichiers uploadés (dev)
```

---

## 🤝 Contribuer

* Style Python : PEP8 (black/isort si souhaité).
* PR bienvenues : UI, accessibilité, tests, intégration CI/CD.
* Idées : pagination native sur listes, filtres avancés projets/blog, recherche full-text, RSS, i18n complète.

---

## 👤 Auteurs & crédits

* **ANNOOR** — Ingénierie • Industriel • Travaux Publics
* Dév/Intégration : **Issaka Hama Barhamou**

  * LinkedIn : [https://www.linkedin.com/in/barhamou-issaka-hama-90047b179/](https://www.linkedin.com/in/barhamou-issaka-hama-90047b179/)
  * GitHub : [https://github.com/HamaBarhamou](https://github.com/HamaBarhamou)

---

## 📄 Licence

Ce projet est fourni “as-is” pour un usage interne / démonstration. Ajoutez votre licence (MIT/Propriétaire) selon votre contexte.

---

## ⚡ TL;DR

```bash
# 1) Installer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Init DB
python manage.py migrate && python manage.py createsuperuser

# 3) Lancer
python manage.py runserver
# → http://127.0.0.1:8000  (admin: /admin)
```

Prêt à l’emploi. Personnalisez **SiteContact**, **HomeSettings** et publiez vos **services/projets/articles** ✨.

