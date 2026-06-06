from datetime import date, datetime
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape

from .models.litter_pup import LitterPup


LITTER_EXPORT_COLUMNS = [
    "ID#",
    "Male (M)",
    "(Father)",
    "(Mother)",
    "Sex",
    "DOB",
    "Wean Date",
    "Age (Days)",
    "Age (Months)",
    "Genotype Reference #1",
    "Genotype Reference #2",
]


def cell_ref(row_index: int, column_index: int):
    column_name = ""
    current = column_index
    while current:
        current, remainder = divmod(current - 1, 26)
        column_name = chr(65 + remainder) + column_name
    return f"{column_name}{row_index}"


def cell_xml(row_index: int, column_index: int, value):
    if value is None:
        value = ""
    if isinstance(value, (date, datetime)):
        value = value.isoformat()

    ref = cell_ref(row_index, column_index)
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'


def row_xml(row_index: int, values):
    cells = "".join(
        cell_xml(row_index, column_index, value)
        for column_index, value in enumerate(values, start=1)
    )
    return f'<row r="{row_index}">{cells}</row>'


def age_days(dob: date | None):
    return (date.today() - dob).days if dob else None


def age_months(dob: date | None):
    if dob is None:
        return None
    today = date.today()
    months = (today.year - dob.year) * 12 + today.month - dob.month
    if today.day < dob.day:
        months -= 1
    return max(months, 0)


def pup_row(pup: LitterPup):
    sire = pup.mating.sire
    dam = pup.mating.dam
    return [
        pup.assigned_external_id or (pup.mouse.external_id if pup.mouse else ""),
        "M" if pup.sex.lower().startswith("m") else "",
        sire.external_id or sire.id,
        dam.external_id or dam.id,
        pup.sex,
        pup.dob,
        pup.wean_date,
        age_days(pup.dob),
        age_months(pup.dob),
        pup.genotype_reference_1,
        pup.genotype_reference_2,
    ]


def build_litter_history_xlsx(pups: list[LitterPup]):
    rows = [row_xml(1, LITTER_EXPORT_COLUMNS)]
    rows.extend(
        row_xml(row_index, pup_row(pup))
        for row_index, pup in enumerate(pups, start=2)
    )

    sheet_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>{''.join(rows)}</sheetData>
</worksheet>"""

    workbook_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Litter History" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>"""

    workbook_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""

    root_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""

    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", content_types_xml)
        workbook.writestr("_rels/.rels", root_rels_xml)
        workbook.writestr("xl/workbook.xml", workbook_xml)
        workbook.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        workbook.writestr("xl/worksheets/sheet1.xml", sheet_xml)

    output.seek(0)
    return output
