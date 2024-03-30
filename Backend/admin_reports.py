from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from report_generation import generate_events_by_date_range_report
from pydantic import BaseModel
from typing import Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from datetime import datetime

app = FastAPI()

class DateRange(BaseModel):
    start_date: str
    end_date: str

def generate_events_by_date_range_report(start_date, end_date):
    # Generate the report data
    data = [['Event Title', 'Event Date', 'Venue']]
    # Retrieve events from database and populate data

    # Create PDF report
    doc = SimpleDocTemplate("events_report.pdf", pagesize=letter)
    header = Paragraph("Family Snapshot", style=ParagraphStyle(name='HeaderStyle', fontSize=14))
    footer = Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                       style=ParagraphStyle(name='FooterStyle', fontSize=10))
    table = Table(data)
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    table.setStyle(style)
    elements = [header, table, footer]
    doc.build(elements)

@app.post("/generate_events_report")
async def generate_events_report(date_range: DateRange):
    try:
        generate_events_by_date_range_report(date_range.start_date, date_range.end_date)
        return FileResponse("events_report.pdf", media_type="application/pdf", filename="events_report.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


