# Lodgo — Hotel Booking App

> A full-stack hotel booking web application with search, reservations, payments, and reviews.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-TypeScript-61DAFB?style=flat&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start (Demo)](#quick-start-demo)
- [Production Deployment](#production-deployment)

---

## Overview

Lodgo is a pet project — a hotel booking website where users can search for hotels, book rooms, pay for reservations, and leave reviews. The backend is built with Python 3.11 and FastAPI, the frontend with React + TypeScript.

---

## Features

- **Hotel Search** — filter by city, check-in/check-out dates, and number of guests
- **Filtering** — filter results by price range, rating, and facilities
- **Booking** — reserve a room with a 10-minute payment window before auto-cancellation
- **Payment** — card validation flow that confirms the reservation
- **Auto-cancellation & Completion** — handled automatically via Celery background tasks
- **Reviews** — users can leave a review only after a completed stay
- **Favorites** — save hotels to a personal favorites list
- **Authentication** — registration with email confirmation, JWT via HttpOnly cookies with auto-refresh

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy, Alembic, Celery |
| Frontend | React, TypeScript, Redux Toolkit, Tailwind CSS |
| Database | PostgreSQL |
| Cache / Queue | Redis |
| Infrastructure | Docker, Docker Compose, Nginx |

---

## Project Structure

```
Lodgo/
├── backend/
│   ├── auth/               # login, register, JWT, dependencies, email verification
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   ├── dependencies.py
│   │   └── email_utils.py
│   ├── hotels/             # hotels, rooms, facilities, services, favorites, images
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── bookings/           # create, pay, cancel, complete bookings
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── reviews/            # create and list reviews
│   │   ├── router.py
│   │   └── schemas.py
│   ├── alembic/            # database migrations
│   ├── media/              # uploaded hotel and room images
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── config.py
│   ├── celery_app.py
│   ├── tasks.py            # background: rating cache, auto-cancel, auto-complete
│   ├── seed.py
│   ├── entrypoint.sh       # runs migrations and seed on container start
│   ├── Dockerfile
│   └── example.env
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/     # Avatar, Notify, StarRating
│   │   ├── layouts/        # MainLayout, EmptyLayout
│   │   ├── pages/          # Home, Hotels, Hotel, Profile, CreateBooking, PayBooking, Login, Register, VerifyEmail, RoomModal
│   │   ├── ts/             # store, authSlice, axiosInstance, types
│   │   ├── utils/          # formatBookingDates
│   │   └── App.tsx
│   ├── example.env
│   └── vite.config.ts
├── nginx/
│   ├── Dockerfile              # demo build
│   ├── Dockerfile.prod         # production build
│   ├── nginx.conf              # demo config (HTTP only)
│   └── nginx.prod.conf         # production config (HTTP + certbot challenge)
├── docker-compose.yml          # production
├── docker-compose.demo.yml     # demo (quick start)
├── .env                        # postgres credentials for docker-compose
└── example.env                 # template
```

---

## Quick Start (Demo)

For anyone who wants to run the project locally and explore all features immediately.

**1. Clone the repository**

```bash
git clone https://github.com/Dzekrajkan/Lodgo
cd Lodgo
```

**2. Create the root `.env` file**

```bash
cp example.env .env
```

The default values in `example.env` work out of the box — no changes needed.

**3. Create the backend `.env` file**

```bash
cp backend/example.env backend/.env
```

**4. Create the frontend `.env` file**

```bash
cp frontend/example.env frontend/.env
```

**5. Start the containers**

```bash
docker compose -f docker-compose.demo.yml up --build
```

Wait for all services to start (about 2–3 minutes on first build).

That's it — the app will be available at `http://localhost`.

> On startup, the container automatically runs Alembic migrations and seeds the database via `entrypoint.sh`. No manual steps needed.

**Test accounts:**

| Email | Password |
|---|---|
| `test@gmail.com` | `test1234` |
| `alex@example.com` | `alex1234` |

---

> **Email confirmation** — registration requires email confirmation. To enable it, fill in your mail credentials in `backend/.env`. Without this, use the test accounts above.
>
> Gmail users: generate an App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) and use it as `MAIL_PASSWORD`.

---

## Production Deployment

For deploying on a VPS with a real domain and HTTPS via Let's Encrypt.

**1. Clone and set up env files**

```bash
git clone https://github.com/Dzekrajkan/Lodgo
cd Lodgo
cp example.env .env
cp backend/example.env backend/.env
cp frontend/example.env frontend/.env
```

Edit `.env` with your real Postgres credentials.

Edit `backend/.env` with production values:
- `SECRET_KEY` — a long random string
- `COOKIE_SECURE=true`
- `CORS_ORIGINS` — your domain, e.g. `https://yourdomain.com`
- `VEREFI_EMAIL_URL` — your domain, e.g. `https://yourdomain.com`
- Mail credentials

Edit `frontend/.env`:
```dotenv
VITE_API_URL=/api
VITE_IMAGE_HOST_URL=yourdomain.com
```

**2. Update the nginx config with your domain**

In `nginx/nginx.prod.conf`, replace `yourdomain.com` with your actual domain:

```nginx
server_name yourdomain.com www.yourdomain.com;
```

**3. Start the containers (HTTP only first)**

```bash
docker compose up --build -d
```

**4. Obtain SSL certificate**

```bash
docker compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your@email.com \
  --agree-tos \
  --no-eff-email \
  -d yourdomain.com -d www.yourdomain.com
```

**5. Update nginx config for HTTPS**

After getting the certificate, replace the contents of `nginx/nginx.prod.conf` with:

```nginx
events {}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /assets/ {
            try_files $uri =404;
        }

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

**6. Rebuild nginx**

```bash
docker compose up --build -d nginx
```

The site is now running at `https://yourdomain.com`.

> Certificates auto-renew every 12 hours via the `certbot` container.