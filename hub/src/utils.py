from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import os
from datetime import datetime
import requests

PDF_DIR = "./pdfs"
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)


def create_pdf(
    data: any,
    name: str,
    timestamp_start: datetime = None,
    timestamp_end: datetime = None,
) -> FileResponse:
    # Create the PDF file path
    pdf_file = os.path.join(PDF_DIR, f"{name}_calibration_log.pdf")

    # Create the PDF document
    doc = SimpleDocTemplate(pdf_file, pagesize=A4)
    elements = []

    # Add a title
    styles = getSampleStyleSheet()
    timestamps = ""
    if timestamp_start or timestamp_end:
        timestamps = f"{timestamp_start} - {timestamp_end}"
    title = f"Calibration Log for instrument '{name}' {timestamps}"
    elements.append(Paragraph(title, styles["Title"]))

    # Prepare the data for the table (including column headers)
    table_data = [["Instrument Name", "Inspector", "Value", "Timestamp"]]  # Headers
    for entry in data:
        table_data.append(
            [entry.instrument_name, entry.inspector, entry.value, entry.timestamp]
        )

    # Create the table with the data
    table = Table(table_data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),  # Header background
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Add gridlines
            ]
        )
    )

    elements.append(table)

    # Build the PDF
    doc.build(elements)

    # Return the generated PDF as a file response
    return FileResponse(
        path=pdf_file, filename=os.path.basename(pdf_file), media_type="application/pdf"
    )


def convert_dict_to_commands_string(commands: dict):
    new_commands_string = ""
    first = True
    for command, description in commands.items():
        if first:
            new_commands_string += f"{command}:{description}"
        else:
            new_commands_string += f";{command}:{description}"
        first = False
    return new_commands_string


def convert_commands_string_to_dict(commands: str):
    new_dict = {}
    commands_list = commands.split(";")
    for command in commands_list:
        com, description = command.split(":")
        new_dict[com] = description
    return new_dict
