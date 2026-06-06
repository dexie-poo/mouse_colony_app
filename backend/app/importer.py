from datetime import datetime
from io import BytesIO

from openpyxl import load_workbook
from sqlalchemy.orm import Session

from .models.cage import Cage
from .models.mouse import Mouse
from .models.user import User


HEADER_ALIASES = {
    "id#": "external_id",
    "sex": "gender",
    "dob": "dob",
    "age (months)": "age_months",
    "genotype": "genotype",
    "purpose": "purpose",
    "color": "color",
    "barcodes": "cage_number",
}


def normalize_header(value):
    return str(value or "").strip().lower()


def normalize_cell(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def parse_dob(value):
    if value is None:
        return None
    if hasattr(value, "date"):
        return value.date()
    if isinstance(value, str):
        text = value.strip()
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
    return None


def calculate_age_months(dob):
    if dob is None:
        return None

    today = datetime.today().date()
    months = (today.year - dob.year) * 12 + today.month - dob.month
    if today.day < dob.day:
        months -= 1
    return str(max(months, 0))


def get_or_create_cage(db: Session, cage_number: str | None, user_id: int):
    if not cage_number:
        return None

    cage = (
        db.query(Cage)
        .filter(Cage.user_id == user_id, Cage.cage_number == cage_number)
        .first()
    )
    if cage:
        return cage

    cage = Cage(cage_number=cage_number, user_id=user_id)
    db.add(cage)
    db.flush()
    return cage


def import_mice_from_xlsx(content: bytes, db: Session, current_user: User):
    workbook = load_workbook(BytesIO(content), data_only=True)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return 0

    headers = [HEADER_ALIASES.get(normalize_header(value)) for value in rows[0]]
    imported = 0

    for row in rows[1:]:
        values = {
            header: row[index]
            for index, header in enumerate(headers)
            if header and index < len(row)
        }
        if not any(values.values()):
            continue

        dob = parse_dob(values.get("dob"))
        remark_parts = []
        if normalize_cell(values.get("color")):
            remark_parts.append(f"Color: {normalize_cell(values.get('color'))}")
        if normalize_cell(values.get("purpose")):
            remark_parts.append(f"Purpose: {normalize_cell(values.get('purpose'))}")

        cage = get_or_create_cage(
            db,
            normalize_cell(values.get("cage_number")),
            current_user.id,
        )
        age_months = calculate_age_months(dob) or normalize_cell(values.get("age_months"))
        mouse = Mouse(
            user_id=current_user.id,
            external_id=normalize_cell(values.get("external_id")),
            gender=normalize_cell(values.get("gender")) or "Unknown",
            dob=dob,
            age_months=age_months,
            genotype=normalize_cell(values.get("genotype")) or "Unknown",
            owner=current_user.username,
            remark="; ".join(remark_parts) or None,
        )
        if cage:
            mouse.cage = cage

        db.add(mouse)
        imported += 1

    db.commit()
    return imported
