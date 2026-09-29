# AgroTechReshenie — Company Website

Corporate website for **ООО «АгроТехРешение» (AgroTechReshenie LLC)**, a Belarus-based company providing precision heavy-equipment repair (line boring, hardfacing, seized-pin burning, plasma cutting), mechanized cleaning and mowing of territories, and developing the “13 Kvartal” campground.

The site is built with Django and PostgreSQL. All content — texts, photos, reviews, contacts — is editable through the Django admin, so the client can update the site without touching code.

---

## Features

- **Pixel-faithful layout** based on the Figma design (1920 px desktop frame), scaling proportionally on smaller desktop screens.
- **Content managed in the admin**
  - Site settings: hero title/subtitle/background, “About” text, phones, addresses, map coordinates, social links
  - Service categories (home-page cards) with an *“In progress”* status for upcoming directions
  - Services with rich text and a drag-and-drop sortable photo/video gallery
  - Client reviews and the stats counters (500+, 140+ …), also sortable
- **Automatic image optimization** — uploaded photos are rotated by EXIF, downscaled to 1920 px and converted to WebP, plus a 900 px thumbnail. Original 180 MB of phone photos → ~19 MB.
- **Auto-playing galleries** (Swiper) on service pages, with lazy loading of upcoming slides and video support.
- **Yandex Maps** widget in the contacts section; clicking the map opens a route from the visitor’s location to the production site.
- **SEO basics** — per-page titles/descriptions, Open Graph tags, `sitemap.xml`, `robots.txt`, schema.org `LocalBusiness` markup.
- **Production-ready deployment** — Docker Compose with PostgreSQL, Gunicorn, WhiteNoise and Caddy (automatic HTTPS via Let’s Encrypt).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12+, Django 5.2 LTS |
| Database | PostgreSQL 16 |
| Frontend | Django templates, vanilla JS, CSS custom properties, Swiper 11 |
| Fonts | Inter, Oswald (Impact substitute), Carlito (Calibri substitute) — self-hosted |
| Images | Pillow (WebP conversion) |
| Admin | Django admin + django-admin-sortable2 |
| Serving | Gunicorn, WhiteNoise (static), Caddy (reverse proxy, HTTPS, media) |
| Infrastructure | Docker, Docker Compose |

## Project Structure

```
atr/
├── config/                 # Django project: settings, urls, wsgi
├── core/                   # Main app
│   ├── models.py           # SiteSettings, Stat, Category, Service, ServiceMedia, Review
│   ├── admin.py            # Admin configuration (sortable lists & inlines)
│   ├── views.py            # Home, category and service pages
│   ├── images.py           # EXIF rotation, resizing, WebP conversion
│   ├── context_processors.py
│   └── management/commands/seed.py   # Initial content import
├── templates/              # base.html, pages and partials
├── static/
│   ├── css/main.css        # All styles (sizes expressed in 1920 px design units)
│   ├── js/main.js          # Gallery autoplay & lazy loading
│   ├── fonts/              # Self-hosted WOFF2 fonts
│   ├── img/                # Logo and background textures
│   └── vendor/             # Swiper
├── seed/                   # Hero image, category cards, service video for seeding
├── Dockerfile
├── docker-compose.yml      # Production: db + web + caddy
├── docker-compose.dev.yml  # Local development: PostgreSQL only
├── Caddyfile
├── .env.example            # Production environment template
├── .env.local.example      # Local development environment template
└── requirements.txt
```

## URL Map

| URL | Page |
|---|---|
| `/` | Home page |
| `/uslugi/<category>/` | Category page (e.g. `/uslugi/remont/`) |
| `/uslugi/<category>/<service>/` | Service page (e.g. `/uslugi/remont/naplavka-rastochka/`) |
| `/admin/` | Admin panel |
| `/sitemap.xml`, `/robots.txt` | SEO |

---

## Local Development

**Requirements:** Python 3.12+, Docker (for PostgreSQL).

```bash
# 1. Virtual environment and dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Environment
cp .env.local.example .env

# 3. PostgreSQL in Docker (exposed on port 55432 to avoid clashing with a local Postgres)
docker compose -f docker-compose.dev.yml up -d

# 4. Database and content
python manage.py migrate
python manage.py seed --photos "фото сайт"     # path to the client's photo archive
python manage.py createsuperuser

# 5. Run
python manage.py runserver
```

Open http://127.0.0.1:8000 — admin at http://127.0.0.1:8000/admin/.

### Seeding content

`seed` fills the database with the texts from the design and imports photos from the client’s archive. The archive is expected to contain one folder per service:

```
фото сайт/
├── ремонт/          → Line boring & hardfacing
├── выжигалка/       → Seized-pin burning
├── плазменная/      → Plasma cutting
├── косилка/         → Mowing
└── трактор щетка/   → Mechanized cleaning
```

The command is idempotent: re-running it updates texts but keeps existing galleries. Use `--reset-photos` to rebuild galleries from the archive.

> The photo archive is **not** committed to the repository (see `.gitignore`).

---

## Production Deployment (VPS)

**Requirements:** a VPS with Docker and the Docker Compose plugin, a domain whose A record points to the server, ports 80 and 443 open.

```bash
git clone <repository-url> atr && cd atr
cp .env.example .env
nano .env                         # set DOMAIN, SECRET_KEY, ALLOWED_HOSTS, passwords
docker compose up -d --build
```

One-time initialization (upload the photo archive to the server first):

```bash
docker compose run --rm -v "/root/фото сайт:/photos:ro" web python manage.py seed --photos /photos
docker compose exec web python manage.py createsuperuser
```

Caddy obtains and renews the HTTPS certificate automatically.

### Environment variables

| Variable | Description |
|---|---|
| `DEBUG` | `False` in production |
| `SECRET_KEY` | Long random string (`python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DOMAIN` | Primary domain, used by Caddy for HTTPS |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated origins with scheme, e.g. `https://example.by` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Database credentials |
| `DATABASE_URL` | Set automatically in `docker-compose.yml`; set manually for local development |

### Updating

```bash
git pull
docker compose up -d --build
```

Migrations run automatically on container start.

### Backups

```bash
# Database
docker compose exec db pg_dump -U atr atr > backup_$(date +%F).sql

# Uploaded media (Docker volume)
docker run --rm -v atr_media:/media -v "$PWD":/backup alpine tar czf /backup/media_$(date +%F).tar.gz -C /media .
```

---

## Content Editing Guide (Admin)

| Section | What it controls |
|---|---|
| **Настройки сайта** (Site settings) | Hero title, subtitle and background; “About” text; phones; addresses; map coordinates; Instagram/Telegram links |
| **Направления** (Categories) | The three cards on the home page. Status *“В процессе реализации”* makes a card non-clickable |
| **Услуги** (Services) | Page title and text, card image, gallery (drag to reorder; the first photo is the cover), slide interval |
| **Отзывы** (Reviews) | Client reviews; toggle visibility, drag to reorder |
| **Счётчики** (Stats) | Numbers under the hero section |

Photos can be uploaded straight from a phone — they are optimized automatically.

## Roadmap

- [ ] Mobile layout according to the upcoming mobile design
- [ ] Final vector logo
- [ ] Telegram link
- [ ] “13 Kvartal” campground page

## License

Proprietary. © ООО «АгроТехРешение». All rights reserved.
