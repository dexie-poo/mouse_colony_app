# Mouse Colony App

V3.1.1 mouse colony management web application using FastAPI, SQLite or Supabase Postgres, SQLAlchemy, and a lightweight browser frontend.

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
- Import mice from Excel
- View mouse table
- Assign mouse to cage number
- Export current mouse cage list to Excel
- Record mating pairs
- View mating history for any mouse
- Keep or euthanise litters
- Auto-create mouse records for kept pups
- Export separate litter/genotyping history workbook
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
- Individual pup labels
- Individual pup sex
- Individual pup genotyping references
- Individual pup keep/euthanise decision
- Assigned ID# for kept pups
- Auto-created kept mouse IDs
- Notes

The separate litter history export includes:

- ID#
- Male (M)
- Father
- Mother
- Sex
- DOB
- Wean Date
- Age (Days)
- Age (Months)
- Genotype Reference #1
- Genotype Reference #2

Analysis records include:

- Mouse sacrifice date
- Age at sacrifice
- Organs extracted
- Organ conditions
- Picture upload
- Preservation method: FFPE, OCT, or fresh frozen
- Notes

## Excel Import

The import accepts `.xlsx` files with these columns:

```text
Group, ID#, Retag, Sex, Color, DOB, Age (Days), Age (Months), Genotype, Owner, Purpose, Barcodes
```

The importer scans the first 25 rows of every worksheet to find the most likely header row, so the table does not need to start on row 1. It also accepts common column-name variants such as `Mouse ID`, `Gender`, `Date of Birth`, `Cage ID`, and `Cage Number`.

Import mapping:

- `ID#` becomes the displayed mouse ID.
- `Sex` becomes gender.
- `DOB` is imported and age in months is recalculated when possible.
- `Age (Months)` is used only when DOB cannot be parsed.
- `Genotype` becomes genotype.
- `Barcodes` becomes cage number.
- `Color` and `Purpose` are added to remarks.
- `Group`, `Retag`, `Age (Days)`, and spreadsheet `Owner` are ignored.
- Owner is set to the logged-in user who imported the file.

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
