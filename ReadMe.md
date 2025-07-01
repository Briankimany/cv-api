
# 📄 CV-API

A **Flask-based REST API** for managing CV/resume data, featuring:

- User authentication and token handling
- Profile and resume information management
- Modular database access layer

---

## 📚 Documentation

- **API Routes**  
  Available at: [`docs/routes.md`](docs/routes.md)

- **Database Utility Managers**  
  Generated with `pdoc` and available as static HTML files in the `docs` folder on the `docs` branch.

---

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone [https://github.com/Briankimany/cv-api](https://github.com/Briankimany/cv-api.git)
cd CV-API
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac

.\venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the root directory with:

```bash
FLASK_APP=app.backend.api.__init__:init_app
FLASK_DEBUG=1
```

---

## ▶️ Running the API

### Linux/Mac

```bash
export FLASK_APP="app.backend.api.__init__:init_app"
export FLASK_DEBUG=1
flask run
```

### Windows

```cmd
set FLASK_APP=app.backend.api.__init__:init_app
set FLASK_DEBUG=1
flask run
```

---

## 🛠 Optional: `run.sh` Script

Create a `run.sh` file in your project root:

```bash
#!/bin/bash

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables
export FLASK_APP="app.backend.api.__init__:init_app"
export FLASK_DEBUG=1

# Run the app
flask run
```

Make it executable and run:

```bash
chmod +x run.sh
./run.sh
```

---

## 🧪 API Routes Summary

**Base URL**: `<host>/api/1.0/`

### 🔐 Authentication

* `/auth/login` — User login
* `/auth/register` — User registration
* `/auth/token` — Token refresh and management

### 👤 User Profile

* `/user/education` — Manage education details
* `/user/work` — Manage work experience
* `/user/optional` — Manage additional information
* `/user/profile` — View profile data

