# Mouse Colony App

V3.0 mouse colony management web application using FastAPI, SQLite or Supabase Postgres, SQLAlchemy, and a lightweight browser frontend.

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
        analysis.py
        cage.py
        mating.py
        mouse.py
        user.py
      routes/
        __init__.py
        analyses.py
        auth.py
        cages.py
        matings.py
        mice.py
      schemas/
        __init__.py
        analysis.py
        cage.py
        mating.py
        mouse.py
        user.py
  frontend/
    index.html
    styles.css
    script.js
  .gitignore
  README.md
  requirements.txt
```

## Features

- Simple user login and user creation
- Separate mouse colony data per user
- Add mouse
- View mouse table
- Assign mouse to cage number
- Export current mouse cage list to Excel
- Record mating pairs
- View mating history for any mouse
- Keep or euthanise litters
- Auto-create mouse records for kept pups
- Record sacrifice and organ analysis information

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
- Genotyping reference
- Keep/euthanise decision
- Kept pup counts
- Auto-created kept mouse IDs
- Notes

Analysis records include:

- Mouse sacrifice date
- Age at sacrifice
- Organs extracted
- Organ conditions
- Picture upload
- Preservation method: FFPE, OCT, or fresh frozen
- Notes

## V3 Database Note

If you previously ran an older local version, delete the old SQLite file before running V3:

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

## Supabase Database

For deployed data storage, use Supabase Postgres instead of Render's temporary filesystem.

1. Create a Supabase project.
2. In Supabase, open Project Settings > Database.
3. Copy the database connection string.
4. In Render, add an environment variable:

```text
DATABASE_URL=your_supabase_postgres_connection_string
```

The app automatically uses `DATABASE_URL` when it is present. If `DATABASE_URL` is not set, it falls back to local SQLite at `mouse_colony.db`.

If Supabase gives you a URL that starts with `postgresql://` or `postgres://`, the app converts it to the SQLAlchemy driver format automatically.
