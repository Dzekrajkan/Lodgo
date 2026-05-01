# Lodgo - Hotel Booking App

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
- [Installation and Setup](#installation-and-setup)

---

## Overview

Lodgo is a pet project - a hotel booking website where users can search for hotels, book rooms, pay for reservations, and leave reviews. The backend is built with Python 3.11 and FastAPI, and the frontend is written in React + TypeScript.

---

## Features

- **Hotel Search** - filter hotels by city, check-in/check-out dates, and number of guests
- **Booking** - reserve a room with a 10-minute payment window before auto-cancellation
- **Payment** - simple card validation flow that confirms the reservation
- **Auto-cancellation & Completion** - handled automatically via Celery background tasks
- **Reviews** - users can leave a review only after a completed stay at that hotel
- **Authentication** - registration with email confirmation, JWT-based login

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy, Celery |
| Frontend | React, TypeScript |
| Database | PostgreSQL |
| Cache | Redis |
| Infrastructure | Docker, Docker Compose |

---

## Installation and Setup

The entire project runs in Docker - no manual dependency installation needed.

**1. Clone the repository and start the containers**

```bash
docker-compose up --build
```

Or, if you're using a newer version of Docker Compose:

```bash
docker compose up --build
```

Wait about 5 minutes for everything to build and start. The site will be ready at `http://localhost:80`.

---

**2. Configure email (required for new account registration)**

Copy `example.env` and fill in your email credentials so that confirmation emails can be sent:

```dotenv
MAIL_USERNAME=example@gmail.com
MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
MAIL_FROM=example@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

> Don't know where to get these credentials? See the [Google App Passwords guide](https://www.hostpapa.com/knowledgebase/how-to-create-and-use-google-app-passwords/).

---

**3. Seed data & test account**

When the container starts, the database is automatically populated with hotels, rooms, reviews, and test accounts - so you can explore all features right away. See [`backend/seed.py`](./backend/seed.py) for details.

A test account is ready to use:

| Field | Value |
|---|---|
| Email | `test@gmail.com` |
| Password | `test1234` |
