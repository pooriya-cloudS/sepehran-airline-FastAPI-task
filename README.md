# Flights API

This repository contains a production-ready CRUD API for **Flights data management**, built with **FastAPI** and backed by a **MySQL** database.  
The project is fully containerized using Docker and supports automated testing and deployment through CI/CD (GitHub Actions).  
**Project Workflow:** The repository follows the [Gitflow]branching model for all development and release processes.

---

## ✈️ Features

- Python **FastAPI** for fast, documented, modern backend APIs
- **CRUD operations** for `Flight`:
    - Create, Read (with pagination/filter/sort), Update, Soft Delete 
- **MySQL** as persistent data store 
- Structured **JSON** API responses: `{status, message, data}`
- **Type hints** throughout the codebase we use PEP8 approach 
- Robust request validation, error handling with FastAPI & Pydantic
- **OpenAPI** automatically available at `/docs`
- Organized, maintainable codebase
- **Docker** and **Docker Compose** for reproducible deployment
- **GitHub Actions** for continuous integration 
- **Pytest** for automated API endpoint testing

---

## 🗂 Folder Structure

```
.
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   └── flight.py
│   └── db.py
├── tests/
│   └── test_flight.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
└── README.md
```

---

## 🚀 Quick Start

**1. Clone the repository**

```bash
git clone https://github.com/pooriya-cloudS/sepehran-airline-FastAPI-task.git
cd sepehran-airline-FastAPI-task
```

**2. Environment Variables **

- For secure project we use .env file that upload on github secret variable and you can added that with your openion 

**3. Build and launch (Docker Compose)**

```bash
docker-compose up --build
```

- FastAPI app will be available on [http://localhost:8000](http://localhost:8000)
- Swagger/OpenAPI UI at [http://localhost:8000/docs](http://localhost:8000/docs)
- MySQL DB will run in a separate service container

---

## 🛠️ API Overview

- `POST   /flights/create/`              – Create a new flight
- `GET    /flights/`              – List flights (pagination, filtering, sorting supported)
- `PUT    /flights/{flight_id}`   – Update a flight
- `DELETE /flights/delete/{flight_id}`   – Delete a flight with soft delete approach

_All endpoints return a JSON object:_
```json
{
  "status": "success",
  "message": "Flight created successfully.",
  "data": { /* ... */ }
}
```

---

## 🧪 Run Tests

```bash
# inside the container
docker-compose exec app pytest

# or from local Python env
pytest tests/
```

---

## ⚙️ CI/CD Workflow

- On every push or pull request, the **GitHub Actions** workflow `.github/workflows/ci-cd.yml`:
    - Builds Docker containers
    - Installs dependencies
    - Runs all tests (pytest)
    - [Optional: add linting, formatting, deployment steps]

---

## 🔀 Gitflow Branching

This repository uses the [Gitflow workflow]

- Main branches:  
    - `main` (production code)  
    - `develop` (integration of new features)
- Use feature branches (`feature/<feature-name>`) from `develop`
- Use `release/*` and `hotfix/*` as needed

---

## 📬 Submission & Notes


---
