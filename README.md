-----

# Issues & Insights Tracker

Welcome to the Issues & Insights Tracker, a mini SaaS application designed to streamline feedback collection and analytics for clients. This project demonstrates a full-stack application built with SvelteKit, FastAPI, and PostgreSQL, emphasizing clear, idiomatic code and modern development practices.

---

## Table of Contents

- [Features](#features)
- [Technical Stack](#technical-stack)
- [Architecture Overview](#architecture-overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Running with Docker Compose](#running-with-docker-compose)
  - [Running Locally (Development)](#running-locally-development)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
- [API Documentation](#api-documentation)
- [Tests](#tests)
- [Observability](#observability)
- [Bonus Features Implemented](#bonus-features-implemented)
- [Future Improvements](#future-improvements)

---

## Features

The Issues & Insights Tracker provides the following core functionalities:

- **Authentication & Authorization (AuthN/AuthZ):** Secure user authentication using hand-rolled JWTs, supporting email and password login.
- **Role-Based Access Control (RBAC):** Three distinct user roles:
  - **REPORTER:** Can create new issues and view only their own submitted issues.
  - **MAINTAINER:** Can triage any issue, add tags, and update issue statuses.
  - **ADMIN:** Has full CRUD (Create, Read, Update, Delete) capabilities across all issues and users.
- **Issue Management:**
  - Create issues with a **title**, **description** (supporting Markdown with live preview).
  - Attach **optional file uploads** (stored on disk).
  - Define **severity** levels for issues.
  - Manage issue workflow through predefined **statuses**: `OPEN` → `TRIAGED` → `IN_PROGRESS` → `DONE`.
- **Real-time Updates:** Issue lists automatically refresh in real-time when new issues are created or their status changes, leveraging server-sent events (SSE).
- **Interactive Dashboard:** A simple chart visualizes the number of open issues per severity, providing quick insights. Daily issue statistics are also displayed.
- **Background Worker:** A scheduled worker aggregates issue counts by status into a `daily_stats` table every 30 minutes, ensuring up-to-date dashboard data.
- **API Documentation:** Auto-generated OpenAPI (Swagger UI) documentation available at `/api/docs` for easy API exploration.
- **Comprehensive Testing:** Includes unit and integration tests for the backend (achieving \>= 80% coverage) and one end-to-end (E2E) happy path test using Playwright.
- **Containerization:** The entire application stack is containerized using Docker Compose for simplified deployment and environment consistency.
- **Structured Logging:** Implemented structured logging using `loguru` for better insights into application behavior.
- **Metrics:** Basic Prometheus metrics are exposed, specifically for the `create issue` API endpoint.

---

## Technical Stack

The project leverages the following technologies:

- **Frontend:**
  - **SvelteKit:** A powerful framework for building web applications with server-side rendering (SSR) enabled.
  - **Tailwind CSS:** A utility-first CSS framework for rapid and consistent styling.
- **Backend:**
  - **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **Database:**
  - **PostgreSQL 15+:** A robust, open-source relational database.
  - **SQLAlchemy:** The Python SQL toolkit and Object Relational Mapper (ORM) used for database interactions.
  - **Alembic:** A lightweight database migration tool for SQLAlchemy.
- **Containerization:**
  - **Docker Compose:** For defining and running multi-container Docker applications.
- **Authentication:**
  - **JWT (JSON Web Tokens):** For secure, stateless authentication.
- **Real-time Communication:**
  - **Server-Sent Events (SSE):** For efficient real-time updates from the backend to the frontend.
- **Testing:**
  - **Playwright:** For end-to-end browser automation tests.
- **Logging:**
  - **Loguru:** For structured and enhanced logging.
- **Monitoring:**
  - **Prometheus:** For collecting and exposing metrics.

---

## Architecture Overview

The Issues & Insights Tracker follows a standard client-server architecture.

- The **Frontend (SvelteKit)** interacts with the **Backend (FastAPI)** through RESTful APIs and subscribes to SSE for real-time updates.
- The **Backend** communicates with the **PostgreSQL** database via SQLAlchemy.
- A separate **worker service** periodically runs background tasks (like aggregating daily statistics).
- All components are orchestrated using **Docker Compose**, providing a consistent and isolated development and deployment environment.
- `nginx` is optionally considered for production deployments but not explicitly included in the provided `docker-compose.yml`.

<!-- end list -->

```
+----------------+       +----------------+       +-------------------+
|    Frontend    |       |     Backend    |       |    PostgreSQL     |
|   (SvelteKit)  |<----->|    (FastAPI)   |<----->|     (Database)    |
|                |       |                |       |                   |
+----------------+       +-------^--------+       +-------------------+
        ^                        |
        |                  (SSE/WebSockets)
        |                        |
        +------------------------+
        (Real-time updates)

+----------------+
| Background     |
| Worker         |<------(Periodically queries)
| (FastAPI/Celery)|
+----------------+

(All contained within Docker Compose)
```

---

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Ensure you have the following installed:

- [Docker](https://www.docker.com/get-started/) (for Docker Compose)
- [Python 3.9+](https://www.python.org/downloads/) (for local backend development)
- [Node.js](https://nodejs.org/en/download/) (LTS recommended) and [pnpm](https://pnpm.io/installation) (for local frontend development)

### Running with Docker Compose

This is the recommended way to run the entire application stack.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/TanX-009/issues-insights-tracker.git
    cd issues-insights-tracker
    ```

2.  **Create Backend Environment File:**
    Navigate to the `backend/` directory and create a file named `.env`. Populate it with the following environment variables:

    ```env
    # backend/.env
    POSTGRES_USER=your_postgres_user
    POSTGRES_PASSWORD=your_postgres_password
    POSTGRES_DB=issues_db
    POSTGRES_PORT=5432
    POSTGRES_HOST=db # 'db' when running with docker-compose, 'localhost' for local development

    JWT_SECRET=a_very_secure_secret_key_for_jwt_signing
    ACCESS_TOKEN_EXPIRE_MINUTES=60 # Token expiration time in minutes

    DEFAULT_ADMIN_EMAIL=admin@example.com
    DEFAULT_ADMIN_PASSWORD=adminpassword
    ```

> [!NOTE]
> Replace placeholders with strong, unique values, especially for `JWT_SECRET`.

3.  **Create Frontend Production Environment File:**
    Navigate to the `frontend/` directory and create a file named `.env.production`. Populate it with the following environment variables:

    ```env
    # frontend/.env.production
    PUBLIC_API_URL=http://backend:8000
    PUBLIC_SSE_URL=http://localhost:8000
    PROTOCOL_HEADER=x-forwarded-proto
    HOST_HEADER=x-forwarded-host
    ORIGIN=http://localhost:3000
    SECURE_COOKIES=false # Set to true for HTTPS in production
    ```

> [!WARNING]
> Important for `PUBLIC_API_URL`: If you are running Docker Compose and want to access the application via `localhost:3000` from your host machine for development or testing, you need to set `PUBLIC_API_URL=http://backend:8000` and `PUBLIC_SSE_URL=http://localhost:8000` in `frontend/.env.production` .

4.  **Build and Run with Docker Compose:**
    From the root directory of the project, execute:

    ```bash
    docker compose up --build -d
    # Or if you use podman:
    # podman-compose up --build -d
    ```

    This command will build the Docker images for the frontend, backend, and worker, create the database container, and start all services in detached mode (`-d`).

5.  **Access the Application:**
    Once all services are up and running, open your web browser and navigate to `http://localhost:3000`.

    You can log in with the default admin credentials specified in `backend/.env` (e.g., `admin@example.com` / `adminpassword`).

6.  **Access Prometheus Metrics:**
    Prometheus metrics for the backend can be found at `http://localhost:8001`.

### Running Locally (Development)

If you prefer to run services individually for easier development and debugging, follow these steps.

#### Backend Setup

1.  **Navigate to the backend directory:**

    ```bash
    cd backend/
    ```

2.  **Create Backend Environment File:**
    Create a file named `.env` in the `backend/` directory. Populate it with the following environment variables:

    ```env
    # backend/.env
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=issues_db
    POSTGRES_PORT=5432
    POSTGRES_HOST=localhost # 'localhost' for local development

    JWT_SECRET=supersecretkey # Use a strong, unique secret
    ACCESS_TOKEN_EXPIRE_MINUTES=60

    DEFAULT_ADMIN_EMAIL=admin@email.com
    DEFAULT_ADMIN_PASSWORD=admin
    ```

3.  **Start a PostgreSQL Database:**
    Ensure a PostgreSQL instance is running on `localhost:5432` with the credentials specified in your `.env` file. You can use Docker for this:

    ```bash
    docker run --name issues-tracker-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=issues_db -p 5432:5432 -d postgres:15
    ```

4.  **Create virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate # for bash for other shells or windows use appropriate source files
    ```

5.  **Install Python Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

6.  **Run Database Migrations:**

    ```bash
    alembic upgrade head
    ```

7.  **Start the Backend API:**

    ```bash
    fastapi dev main.py
    ```

    The backend API will be accessible at `http://localhost:8000`.
    The prometheus API will be accessible at `http://localhost:8001`.

8.  **Start the Daily Stats Worker (in a separate terminal):**

    ```bash
    python worker.py
    ```

#### Frontend Setup

1.  **Navigate to the frontend directory:**

    ```bash
    cd frontend/
    ```

2.  **Create Frontend Local Environment File:**
    Create a file named `.env.local` in the `frontend/` directory. Populate it with the following environment variables:

    ```env
    # frontend/.env.local
    PUBLIC_API_URL=http://localhost:8000
    PUBLIC_SSE_URL=http://localhost:8000
    SECURE_COOKIES=false
    ```

3.  **Install Node.js Dependencies:**

    ```bash
    pnpm install
    ```

4.  **Start the Frontend Development Server:**

    ```bash
    pnpm run dev
    ```

    The frontend application will be accessible at `http://localhost:5173`.

---

## API Documentation

The backend API is documented using OpenAPI (Swagger UI). Once the backend is running (either via Docker Compose or locally), you can access the interactive API documentation at:

`http://localhost:8000/api/docs`

---

## Tests

The project includes comprehensive tests to ensure correctness and stability.

- **Frontend E2E Tests:**
  End-to-end tests are written using Playwright. To run them (from the `frontend/` directory):

  ```bash
  pnpm run test:e2e      # Run tests in headless mode
  pnpm run test:e2e:headed # Run tests in headed mode (shows browser UI)
  ```

  Ensure the full application stack (backend, frontend, DB) is running before executing E2E tests.

---

## Observability

- **Structured Logging:** The backend uses `loguru` for structured logging, making it easier to parse and analyze logs.
- **Prometheus Metrics:** A basic Prometheus metric is exposed for the `create issue` API endpoint. You can access these metrics at `http://localhost:8001` when running with Docker Compose.

---

## Bonus Features Implemented

The following bonus features have been implemented:

- **Optional File Download:** Uploaded files can be downloaded from the issue detail page.
- **Dark Mode Toggle:** A toggle is available in the UI to switch between light and dark themes.
- **User Management (Admin):** An admin user can perform CRUD operations on other users.
- **Markdown Preview:** The issue description field provides a real-time Markdown rendered preview.

---

## Future Improvements

While the current implementation meets the requirements, here are some areas for future enhancements:

- **S3-compatible Storage:** Integrate with S3 or a similar cloud storage service for file uploads instead of local disk storage for better scalability and resilience.
- **Enhanced Real-time:** Explore WebSockets for more advanced real-time features, such as collaborative editing or live chat on issues.
- **Advanced Dashboard:** Add more complex charts and filtering options to the dashboard for deeper insights.
- **Email Notifications:** Implement email notifications for status changes or new issue assignments.
- **Full-text Search:** Add full-text search capabilities for issues.
