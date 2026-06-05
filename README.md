# Mouse Colony App

V2 mouse colony management web application using FastAPI, SQLite, SQLAlchemy, and a lightweight browser frontend.

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
        mating.py
        mouse.py
      routes/
        __init__.py
        cages.py
        matings.py
        mice.py
      schemas/
        __init__.py
        cage.py
        mating.py
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
- Assign mouse to cage number
- Export current mouse cage list to Excel
- Record mating pairs
- View mating history for any mouse

Mouse identifiers:

- MiceID
- Gender
- DOB
- Age (Months)
- Genotype
- Owner
- Remark
- Cage Number

Each cage has a simple cage number. Multiple mice can be assigned to the same cage number.
Each mouse has one current cage assignment. Assigning that mouse to another cage number transfers the mouse to the new cage.
Age in months is calculated automatically from DOB.

Mating records include:

- Sire
- Dam
- Mating date
- Pup DOB
- Litter size
- Male pups
- Female pups
- Pup genotypes
- Notes

## V2 Database Note

If you previously ran V1 locally, delete the old SQLite file before running V2:

```powershell
Remove-Item backend\mouse_colony.db -ErrorAction SilentlyContinue
```

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

## Deploy On Render

Use these settings for a Render web service:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

The included `render.yaml` contains the same settings.
