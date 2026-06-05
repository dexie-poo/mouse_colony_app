# Mouse Colony App

V1 mouse colony management web application using FastAPI, SQLite, SQLAlchemy, and a lightweight browser frontend.

## Project Structure

```text
mouse_colony_app/
  backend/
    requirements.txt
    app/
      __init__.py
      database.py
      main.py
      models/
        __init__.py
        cage.py
        mouse.py
      routes/
        __init__.py
        cages.py
        mice.py
      schemas/
        __init__.py
        cage.py
        mouse.py
  frontend/
    index.html
    styles.css
    script.js
  .gitignore
  README.md
  requirements.txt
```

## Features

- Add mouse
- View mouse table
- Add cage
- Assign mouse to cage

Mouse identifiers:

- ID
- Genotype
- Gender
- Project
- DOB
- Age
- Age Analysed
- Notes

## Setup

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

## Run Backend

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Run Frontend

Open `frontend/index.html` in a browser after the backend is running.

You can also start the backend from the project root with:

```powershell
.\run_backend.ps1
```
