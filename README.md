# CSEA Event Management System Backend

This repository contains the backend implementation for the CSEA Event Management System recruitment task. It is a production-grade REST API built to handle student registrations and event management concurrently and securely.

## 🚀 Live URL
**Base API URL:** `http://event-mgmt-alb-128175278.us-east-1.elb.amazonaws.com`
**Interactive API Docs (Swagger UI):** `http://event-mgmt-alb-128175278.us-east-1.elb.amazonaws.com/docs`

> *Note: The AWS infrastructure might be spun down after evaluation to save costs.*

---

## 🛠️ Tech Stack & Architecture

This backend was built with scalability, concurrency, and cloud-native principles in mind.

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Framework** | FastAPI (Python 3.12) | High performance, async by default, automatic OpenAPI documentation. |
| **Database** | PostgreSQL 16 (AWS RDS) | Relational integrity, ACID compliance, and robust locking mechanisms. |
| **Caching** | Redis 7 (AWS ElastiCache) | Cache-aside pattern for fast event listing and pagination. |
| **ORM** | SQLAlchemy 2.0 (Async) | Safe query building and async database sessions. |
| **Validation** | Pydantic v2 | Strict request/response schema validation. |
| **Auth** | JWT & bcrypt (passlib) | Stateless, secure endpoint protection. |
| **Infra as Code** | Terraform | Reproducible AWS deployments (VPC, ALB, ECS, RDS, ElastiCache). |
| **Deployment** | Docker & AWS ECS Fargate | Serverless container execution with auto-scaling. |

---

## 💾 Database Design

The database consists of three primary tables with enforced referential integrity and cascading deletes.

1.  **`students`**: Stores student credentials securely (`password_hash` using bcrypt). Email is unique.
2.  **`events`**: Stores event details, `max_capacity`, and tracks `current_registered`.
3.  **`event_registrations`**: A junction table linking students to events. Features a **composite unique constraint** on `(student_id, event_id)` to prevent double registration.

### Concurrency Handling (Pessimistic Locking)
To prevent race conditions where multiple students try to register for the last available slot simultaneously, the registration endpoint uses **pessimistic locking** (`SELECT ... FOR UPDATE`). This locks the specific event row during the transaction, ensuring exact capacity limits are respected.

---

## 📂 Project Structure

```
event-management-system/
├── src/                        # FastAPI Application Code
│   ├── app/
│   │   ├── api/v1/endpoints/   # REST endpoints (auth, events)
│   │   ├── core/               # App config, database setup, JWT security
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic validation schemas
│   │   └── services/           # Business logic & caching layer
│   ├── main.py                 # Application entry point
│   ├── Dockerfile              # Multi-stage production build
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment variables template
│
└── terraform/                  # AWS Infrastructure as Code
    ├── main.tf, variables.tf   # Provider & variables
    ├── vpc.tf, ecr.tf, alb.tf  # Networking, Load Balancer, Registry
    └── ecs.tf, rds.tf, elasticache.tf # Fargate, Postgres, Redis configs
```

---

## 🔌 API Documentation

The complete interactive API documentation (Swagger UI) is automatically generated and available at `/docs` on the live URL.

### Implemented Endpoints:
*   `POST /api/v1/students/register` - Register a new student.
*   `POST /api/v1/students/login` - Authenticate and receive a JWT.
*   `POST /api/v1/events` - Create a new event (Requires Auth).
*   `GET /api/v1/events` - Get all events (Paginated, Cached in Redis).
*   `GET /api/v1/events/{id}` - Get event details.
*   `PUT /api/v1/events/{id}` - Update an event (Requires Auth).
*   `DELETE /api/v1/events/{id}` - Delete an event (Requires Auth).
*   `POST /api/v1/events/{id}/register` - Register current student for an event (Requires Auth, respects capacity limits).
*   `GET /api/v1/events/{id}/participants` - List all registered students for an event (Requires Auth).

---

## ⚙️ Setup and Execution Instructions

### Option 1: Local Development (Without Docker)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Arshad-nr/event-management-system.git
    cd event-management-system/src
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables:**
    Copy `.env.example` to `.env` and fill in your local PostgreSQL and Redis URLs.
    ```env
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/eventdb
    REDIS_URL=redis://localhost:6379/0
    JWT_SECRET_KEY=your_super_secret_key
    ```
4.  **Run the application:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

### Option 2: AWS Deployment (Terraform + ECS)

The `terraform/` directory contains complete Infrastructure-as-Code to spin up a production environment on AWS.

1.  **Deploy Infrastructure:**
    ```bash
    cd terraform
    terraform init
    terraform apply -var="db_password=YOUR_PASS" -var="jwt_secret_key=YOUR_SECRET"
    ```
2.  **Build & Push Docker Image:**
    ```bash
    cd ../src
    docker build -t event-mgmt .
    docker tag event-mgmt:latest <ECR_REPO_URL>:latest
    docker push <ECR_REPO_URL>:latest
    ```
3.  **Update ECS Service:**
    ```bash
    aws ecs update-service --cluster event-mgmt-cluster --service event-mgmt-service --force-new-deployment
    ```

---

## ⚠️ Assumptions and Limitations

*   **Role-Based Access Control (RBAC):** Currently, any authenticated student can create, update, or delete events. In a real-world scenario, an `is_admin` or `role` flag should be added to restrict these actions to organizers only.
*   **Database Migrations:** Tables are currently created automatically via SQLAlchemy's `metadata.create_all()` on application startup for simplicity. For a strict production environment, a tool like Alembic should be used for schema migrations.
*   **Rate Limiting:** No API rate limiting is currently implemented.

---

## 📸 Demonstration

### Screenshots
*(Please refer to the `assets/` folder in this repository for screenshots of the code, database schema, and API testing.)*

### Demo Video
*(Link to the demo video walking through the codebase and API testing via Postman/Swagger)*

---
*Developed for CSEA Recruitment Task*
