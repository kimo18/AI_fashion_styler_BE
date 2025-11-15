Prequsistsis 

pip install uv

uv sync 

activate the venv created

if added a new dependacies via UV add , make sure to put it in requirement.txt using uv pip freeze > requirements.txt (inside the venv)



# **AI Fashion Styler — Backend**

This is the backend service for the **AI Fashion Styler** project, built with **FastAPI**, **PostgreSQL**, and **UV** for dependency management.  
It provides all backend API endpoints, authentication, and database communication for the application.

---

## 🔧 Tech Stack

- **FastAPI**
- **PostgreSQL**
- **UV** (dependency management)
- **Uvicorn**
- **Docker & Docker Compose**
- **Async SQL (asyncpg)**

---

# 🚀 Prerequisites & Setup

Make sure you have:

- Python **3.12+**
- **UV** installed
- (Optional) Docker + Docker Compose

---

# 📦 Environment Setup Using UV

### **1. Install UV**
```bash
pip install uv
uv sync
```
Make sure you activate the built venv folder.


# 📦 Run the Backend

### **Option 1. On Host**

```bash
UV run ./main
```
### **Option 2. Using docker**

Make sure that docker is installed on your system, then build and run the docker container

```bash
docker-compose up --build
```

HAVE fun little Mnhy



