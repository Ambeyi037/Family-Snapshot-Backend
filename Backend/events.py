from fastapi import APIRouter,status,Depends,HTTPException,Response,Query
from .schemas import insert_events,show_events,show_person
from .models import Events
from sqlalchemy.orm import Session
from .utils import get_db,hash
from reportlab.platypus import Spacer 
from typing import List
from .tokgen import get_current_user
from passlib.context import CryptContext
from typing import List
from datetime import datetime
from datetime import datetime, date, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Frame,Paragraph, PageTemplate,BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import Paragraph, PageTemplate
from io import BytesIO
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse

router_Events=APIRouter(tags= ['Events'])

@router_Events.post("/post_event", status_code=status.HTTP_201_CREATED)
def post_event(request: insert_events, db: Session = Depends(get_db)):
    event_data = request.dict()
    event_data['created_at'] = datetime.now()
    print(event_data)
    event = Events(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event    

@router_Events.get("/events",status_code=status.HTTP_302_FOUND) 
def get_events(db:Session=Depends(get_db)):
    memories=db.query(Events).all() 
    if not memories:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="No content")
    return memories 

# ,response_model=show_events
@router_Events.get("/event/{id}",status_code=status.HTTP_302_FOUND) 
def get_event(id: int,db:Session=Depends(get_db)):
    event=db.query(Events).filter(Events.event_id==id).first() 
    if not event:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="No content")
    return event    
# {{URL}}specific_user_events/48
@router_Events.get("/specific_user_events/{creator_id}",status_code=status.HTTP_302_FOUND) 
def get_event1(creator_id: int,db:Session=Depends(get_db)):
    events=db.query(Events).filter(Events.created_by==creator_id).all() 
    if not events:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="No Events for this user")
    return events       

   
# {{URL}}specific_user_events/48
@router_Events.get("/specific_user_events/{creator_id}",status_code=status.HTTP_302_FOUND) 
def get_event1(creator_id: int,db:Session=Depends(get_db)):
    events=db.query(Events).filter(Events.created_by==creator_id).all() 
    if not events:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="No Events for this user")
    return events        

# ,current_user : int = Depends(get_current_user)
@router_Events.delete("/delete_event/{id}",status_code=status.HTTP_202_ACCEPTED)
def delete_event(id : int,db:Session=Depends(get_db)):
    # print(current_user.id)
    event=db.query(Events).filter(Events.event_id==id)
    print("pass")
    if event.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"detail":f"Person id {id} does not exist"})     
    event.delete(synchronize_session=False)
    db.commit() 
    return Response(status_code=status.HTTP_204_NO_CONTENT)




# Generate events report PDF
def generate_events_report(events):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    event_data = [["Event Title", "Host", "Venue", "Event Date"]]

    for event in events:
        event_data.append([
            event.event_title,
            f"{event.f_name} {event.surname}",
            event.venue,
            event.event_date.strftime("%Y-%m-%d")
        ])

    table = Table(event_data)
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    table.setStyle(style)
    elements = [table]
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# FastAPI route to download events report between two dates
@router_Events.get("/download_events_report/")
def download_events_report(start_date: datetime = Query(..., description="Start date in format YYYY-MM-DD"),
                            end_date: datetime = Query(..., description="End date in format YYYY-MM-DD"),db:Session=Depends(get_db)):
    try:
        events = db.query(Events).filter(Events.event_date.between(start_date, end_date)).all()
        if not events:
            raise HTTPException(status_code=404, detail="No events found in the specified date range")
        
        pdf_data = generate_events_report(events)
        db.close()
        return {"filename": "events_report.pdf", "data": pdf_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router_Events.get("/monthly_events_report/")
def download_events_report(db:Session=Depends(get_db)):
    today = date.today()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = today.replace(day=1) + timedelta(days=32) - timedelta(days=1)
    try:
        events = db.query(Events).filter(Events.event_date.between(first_day_of_month, last_day_of_month)).all()
        if not events:
            raise HTTPException(status_code=404, detail="No events found in the current month")
        
        pdf_data = generate_events_report(events)
        db.close()
        return {"filename": "events_report.pdf", "data": pdf_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


def generate_events_report1(events):
    buffer = BytesIO()

    # Define header and footer styles
    styles = getSampleStyleSheet()
    header_style = styles['Italic']
    footer_style = styles['Normal']

    # Define header and footer content
    header_text = Paragraph(f"This Report was produced by Family Snapshot on {datetime.now().strftime('%Y-%m-%d')}", header_style)
    footer_text = Paragraph("Contact information, 1234-Nairobi, Kasarani Drive-in<br/>Contact email: familysnapshot@hotmail.com", footer_style)

    # Define header and footer frames
    header_frame = Frame(72, 730, 460, 50, id='header', showBoundary=0)
    footer_frame = Frame(72, 40, 460, 50, id='footer', showBoundary=0)

    # Define the page template with header and footer
    page_template = PageTemplate(id='report', frames=[header_frame, footer_frame])

    # Define the document template with the page template
    doc = BaseDocTemplate(buffer, pagesize=letter, pageTemplates=[page_template])

    # Create Story elements
    elements = [header_text]

    # Add events data to the PDF content
    event_data = [["Event Title", "Host", "Venue", "Event Date"]]
    for event in events:
        event_data.append([
            event.event_title,
            f"{event.f_name} {event.surname}",
            event.venue,
            event.event_date.strftime("%Y-%m-%d")
        ])

    table = Table(event_data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(footer_text)

    # Add header and footer to each page
    doc.addPageTemplates([page_template])
    doc.build(elements)

    return buffer.getvalue()

@router_Events.get("/download_events_report1/")
def download_events_report(db:Session=Depends(get_db)):
    today = date.today()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = today.replace(day=1) + timedelta(days=32) - timedelta(days=1)
    try:
        events = db.query(Events).filter(Events.event_date.between(first_day_of_month, last_day_of_month)).all()
        if not events:
            raise HTTPException(status_code=404, detail="No events found in the current month")
        
        pdf_data = generate_events_report(events)
        db.close()
        return StreamingResponse(BytesIO(pdf_data), media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()



@router_Events.get("/download_events_report12/")
async def download_events_report(db:Session=Depends(get_db)):
    today = date.today()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = today.replace(day=1) + timedelta(days=32) - timedelta(days=1)

    try:
        events = db.query(Events).filter(Events.event_date.between(first_day_of_month, last_day_of_month)).all()
        if not events:
            raise HTTPException(status_code=404, detail="No events found in the current month")
        
        pdf_data = generate_events_report1(events)
        db.close()
        return StreamingResponse(BytesIO(pdf_data), media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router_Events.get("/generate_events_report")
async def generate_report(db: Session = Depends(get_db)):
    # Query all events from the database
    events = db.query(Events).all()

    # Generate PDF report
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    # Write report title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 750, "Events Report")
    
    # Write event details
    pdf.setFont("Helvetica", 12)
    y_position = 700
    for event in events:
        pdf.drawString(100, y_position, f"Event Title: {event.event_title}")
        pdf.drawString(100, y_position - 20, f"Host: {event.f_name} {event.surname}")
        pdf.drawString(100, y_position - 40, f"Venue: {event.venue}")
        pdf.drawString(100, y_position - 60, f"Date: {event.event_date}")
        pdf.drawString(100, y_position - 80, f"Time: {event.event_time}")
        pdf.drawString(100, y_position - 100, f"Description: {event.description}")
        y_position -= 120

    pdf.save()
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/pdf", headers={'Content-Disposition': 'attachment; filename="events_report.pdf"'})   




