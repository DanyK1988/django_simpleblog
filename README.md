# Django Simple Blog

A small Django project that implements a classic blog application: create and publish posts, browse posts with pagination, filter by tags, view post details, add comments, and share a post via email.

## Features

- Posts with **draft/published** workflow
- Tagging using `django-taggit`
- Post list with **pagination**
- Post detail page with **active comments**
- Add a new comment (POST)
- “Share by email” form (SMTP)
- Basic Django Admin configuration for `Post` and `Comment`

## Tech stack

- Python (virtualenv in `.venv`)
- Django 6.x
- SQLite (`db.sqlite3`) for local development
- `django-taggit` for tags
- `python-dotenv` for environment variables

## Project structure

```
.
├── manage.py
├── README.md
├── db.sqlite3
├── mysite/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── blog/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   ├── templatetags/
│   │   └── blog_tags.py
│   └── static/
│       └── css/
│           └── blog.css
└── templates/
    ├── pagination.html
    └── blog/
        ├── base.html
        └── post/
            ├── list.html
            ├── detail.html
            ├── share.html
            ├── comment.html
            └── includes/
```

## How it works (high level)

### URL routing

- Project routes (`mysite/urls.py`):
  - `/admin/` – Django admin
  - `/blog/` – includes the blog app routes
- Blog routes (`blog/urls.py`):
  - `/blog/` – post list (supports optional tag filtering)
  - `/blog/tag/<tag>/` – post list filtered by tag
  - `/blog/<yyyy>/<mm>/<dd>/<slug>/` – post detail
  - `/blog/<post_id>/share/` – share a post via email
  - `/blog/<post_id>/comment/` – create a comment (POST)

### Data model

`blog/models.py` defines two main entities:

- **Post**
  - `title`, `slug`, `author`, `body`
  - timestamps: `publish`, `created`, `updated`
  - `status`: Draft (`DF`) / Published (`PB`)
  - `tags`: managed by `django-taggit`
  - custom manager `PublishedManager` exposed as `Post.published` to conveniently query only published posts
- **Comment**
  - belongs to a `Post` (`post.comments`)
  - `name`, `email`, `body`
  - timestamps: `created`, `updated`
  - `active`: allows moderating/hiding comments without deleting them

### Views

`blog/views.py` provides:

- **Post list**: fetches published posts, optionally filters by tag, and paginates (3 posts per page)
- **Post detail**: fetches a published post by date + slug, loads active comments, and computes “similar posts” by shared tags
- **Comment creation**: validates and saves a `Comment` bound to the post (POST-only)
- **Share by email**: validates the form and sends an email containing the absolute URL to the post

### Templates & static files

- Templates live in `templates/` (configured via `TEMPLATES["DIRS"]` in `mysite/settings.py`)
- `templates/pagination.html` provides reusable pagination UI
- Blog templates are under `templates/blog/`
- CSS is in `blog/static/css/blog.css`

## Setup (local development)

### 1) Create virtualenv & install dependencies

If you don’t already have a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install django django-taggit python-dotenv certifi
```

### 2) Configure environment variables

This project expects email credentials in a `.env` file (loaded in `mysite/settings.py`):

```bash
EMAIL_USER=your_smtp_username
EMAIL_PASSWORD=your_smtp_password
```

SMTP is configured for Yandex by default:

- `EMAIL_HOST=smtp.yandex.ru`
- `EMAIL_PORT=465`
- SSL enabled (`EMAIL_USE_SSL=True`)

### 3) Run migrations

```bash
source .venv/bin/activate
python manage.py migrate
```

### 4) Create an admin user

```bash
python manage.py createsuperuser
```

### 5) Run the server

```bash
python manage.py runserver
```

Then open:

- Blog: http://127.0.0.1:8000/blog/
- Admin: http://127.0.0.1:8000/admin/

## Notes / limitations

- `DEBUG=True` and `ALLOWED_HOSTS=[]` are configured for development only.
- SQLite is used for development convenience; switch `DATABASES` for production.
- Don’t commit secrets: keep `.env` local (it is ignored by `.gitignore` in this repo).
