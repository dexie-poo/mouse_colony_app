from datetime import date, datetime
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape

from app.models.mouse import Mouse


EXPORT_COLUMNS = [
    "MiceID",
    "Gender",
    "DOB",
    "Age (Months)",
    "Genotype",
    "Owner",
    "Remark",
    "Cage Number",
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


def mouse_export_row(mouse: Mouse):
    return [
        mouse.id,
        mouse.gender,
        mouse.dob,
        mouse.age_months,
        mouse.genotype,
        mouse.owner,
        mouse.remark,
        mouse.cage_number,
    ]


def build_mouse_export_xlsx(mice: list[Mouse]):
    rows = [row_xml(1, EXPORT_COLUMNS)]
    rows.extend(
        row_xml(row_index, mouse_export_row(mouse))
        for row_index, mouse in enumerate(mice, start=2)
    )

    sheet_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>{''.join(rows)}</sheetData>
</worksheet>"""

    workbook_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Mice Cage List" sheetId="1" r:id="rId1"/>
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
