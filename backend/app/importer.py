from datetime import datetime
from io import BytesIO

from openpyxl import load_workbook
from sqlalchemy.orm import Session

from .models.cage import Cage
from .models.mouse import Mouse
from .models.user import User


HEADER_ALIASES = {
    "id#": "external_id",
    "id": "external_id",
    "mouse id": "external_id",
    "mouseid": "external_id",
    "mice id": "external_id",
    "miceid": "external_id",
    "sex": "gender",
    "gender": "gender",
    "dob": "dob",
    "date of birth": "dob",
    "birth date": "dob",
    "age (months)": "age_months",
    "age months": "age_months",
    "agemonths": "age_months",
    "genotype": "genotype",
    "geno": "genotype",
    "purpose": "purpose",
    "color": "color",
    "barcodes": "cage_number",
    "barcode": "cage_number",
    "cage": "cage_number",
    "cage id": "cage_number",
    "cage number": "cage_number",
    "cage #": "cage_number",
}

COMMON_FIELDS = {"external_id", "gender", "dob", "genotype", "cage_number"}


def normalize_header(value):
    text = str(value or "").strip().lower()
    for old, new in {
        "\n": " ",
        "\r": " ",
        "_": " ",
        "-": " ",
        ":": "",
    }.items():
        text = text.replace(old, new)
    return " ".join(text.split())


def map_header(value):
    normalized = normalize_header(value)
    compact = normalized.replace(" ", "")
    if normalized in HEADER_ALIASES:
        return HEADER_ALIASES[normalized]
    if compact in HEADER_ALIASES:
        return HEADER_ALIASES[compact]

    for alias, field in HEADER_ALIASES.items():
        if alias in normalized:
            return field
    return None


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
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m/%d/%y"):
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


def find_header_row(rows):
    best_index = None
    best_headers = []
    best_score = 0

    for index, row in enumerate(rows[:25]):
        mapped_headers = [map_header(value) for value in row]
        score = len({header for header in mapped_headers if header})
        if score > best_score:
            best_index = index
            best_headers = mapped_headers
            best_score = score

    if best_index is None or best_score < 2:
        return None, []

    return best_index, best_headers


def row_has_mouse_signal(values):
    return any(
        normalize_cell(values.get(field))
        for field in ("external_id", "gender", "genotype", "cage_number")
    ) or parse_dob(values.get("dob"))


def import_mice_from_xlsx(content: bytes, db: Session, current_user: User):
    workbook = load_workbook(BytesIO(content), data_only=True)
    imported = 0
    skipped = 0
    sheets_scanned = 0
    matched_fields = set()

    for sheet in workbook.worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue
        sheets_scanned += 1

        header_index, headers = find_header_row(rows)
        if header_index is None:
            continue

        matched_fields.update(header for header in headers if header)
        for row in rows[header_index + 1 :]:
            values = {
                header: row[index]
                for index, header in enumerate(headers)
                if header and index < len(row)
            }
            if not any(values.values()):
                continue
            if not row_has_mouse_signal(values):
                skipped += 1
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
    return {
        "imported": imported,
        "skipped": skipped,
        "sheets_scanned": sheets_scanned,
        "matched_fields": sorted(matched_fields),
        "missing_common_fields": sorted(COMMON_FIELDS - matched_fields),
    }
