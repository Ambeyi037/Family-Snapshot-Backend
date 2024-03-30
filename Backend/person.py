from fastapi import APIRouter,status,Depends,HTTPException,Response, Query
from .schemas import insert_person,show_person,update_person
from .models import Person,Relationship
from sqlalchemy.orm import Session
from .utils import get_db,hash
from typing import List
from .tokgen import get_current_user
from passlib.context import CryptContext
from sqlalchemy.orm import aliased
from sqlalchemy.sql import case
from sqlalchemy import text
from sqlalchemy import and_
from datetime import datetime, date, timedelta
from sqlalchemy import text
from matplotlib import pyplot as plt
from io import BytesIO
import base64

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Frame,PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle



router_person=APIRouter(tags= ['Person'])


pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")


# ,current_user : str = Depends(get_current_user)
@router_person.post( "/post_person",status_code=status.HTTP_201_CREATED,)
def post_person(request : insert_person,db:Session=Depends(get_db),status_code=status.HTTP_201_CREATED):
    request.password=hash(request.password)
    user=Person(**request.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router_person.post( "/post_spouse/{person_id}",status_code=status.HTTP_201_CREATED,)
def post_person(person_id: int,request : insert_person,db:Session=Depends(get_db),status_code=status.HTTP_201_CREATED):
    request.password=hash(request.password)
    spouse=Person(**request.dict())
    db.add(spouse)
    db.commit()
    db.refresh(spouse)  

    db_person = db.query(Person).filter(Person.id == person_id).first()
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    db_person.spouse_id = spouse.id
    spouse.id=db_person.spouse_id
    db.commit()

    return spouse 


@router_person.post("/post_child/{person_id}", status_code=status.HTTP_201_CREATED)
def post_child(person_id: int, request: insert_person, db: Session = Depends(get_db)):
    request.password = hash(request.password)
    child = Person(**request.dict())
    db.add(child)
    db.commit()
    db.refresh(child)

    # Establish parent-child relationship

    db_person = db.query(Person).filter(Person.id == person_id).first()
    relationship = Relationship(parent_id=person_id, child_id=child.id)
    db.add(relationship)


    if db_person.spouse_id:
        relationship_spouse = Relationship(parent_id=db_person.spouse_id, child_id=child.id)
        db.add(relationship_spouse)

    db.commit()

    return child


@router_person.post("/post_sibling/{person_id}", status_code=status.HTTP_201_CREATED)
def post_sibling(person_id: int, request: insert_person, db: Session = Depends(get_db)):
    request.password = hash(request.password)
    sibling = Person(**request.dict())
    db.add(sibling)
    db.commit()
    db.refresh(sibling)

    # Fetch the original person's parents
    original_person = db.query(Person).filter(Person.id == person_id).first()
    if original_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Establish parent-child relationship for each parent-sibling pair
    for parent in original_person.parents:
        # Fetch other children of the parent to determine if the sibling already exists
        siblings = db.query(Relationship).filter(Relationship.parent_id == parent.id,
                                                  Relationship.child_id != person_id).all()
        for sibling_rel in siblings:
            sibling_id = sibling_rel.child_id
            # Check if the sibling already exists
            existing_sibling = db.query(Person).filter(Person.id == sibling_id).first()
            if existing_sibling.surname == sibling.surname:
                # Establish parent-child relationship between the parent and the existing sibling
                relationship = Relationship(parent_id=parent.id, child_id=sibling_id)
                db.add(relationship)
                db.commit()
                return existing_sibling

    # If the sibling doesn't exist, establish parent-child relationship between the parent and the new sibling
    for parent in original_person.parents:
        relationship = Relationship(parent_id=parent.id, child_id=sibling.id)
        db.add(relationship)
        db.commit()

    return sibling

    
 

@router_person.post("/post_parent/{person_id}", status_code=status.HTTP_201_CREATED)
def post_parent(person_id: int, request: insert_person, db: Session = Depends(get_db)):
    request.password = hash(request.password)
    parent = Person(**request.dict())
    db.add(parent)
    db.commit()
    db.refresh(parent)

    # Establish parent-child relationship between the new parent and the original person
    relationship = Relationship(parent_id=parent.id, child_id=person_id)
    db.add(relationship)
    db.commit()

    return parent   


@router_person.get("/persons_with_relationships",  status_code=status.HTTP_302_FOUND)
def persons_with_relationships(db: Session = Depends(get_db)):
    persons = db.query(Person).all()
    if not persons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No content")

    persons_with_relationships = []
    for person in persons:
        spouses = db.query(Person).filter(Person.id == person.spouse_id).all()
        children = db.query(Person).join(Relationship, Relationship.child_id == Person.id)\
                                    .filter(Relationship.parent_id == person.id).all()
        parents = db.query(Person).join(Relationship, Relationship.parent_id == Person.id)\
                                   .filter(Relationship.child_id == person.id).all()
        siblings = []
        for parent in parents:
            siblings.extend(db.query(Person).join(Relationship, Relationship.parent_id == parent.id)\
                                             .filter(Relationship.child_id != person.id).all())

        persons_with_relationships.append({
            "person": person,
            "spouses": spouses,
            "children": children,
            "parents": parents,
            "siblings": siblings
        })

    return persons_with_relationships



@router_person.get("/person_relationships1/{person_id}", status_code=status.HTTP_200_OK)
def person_relationships(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    spouses = db.query(Person).filter(Person.id == person.spouse_id).all()
    children = db.query(Person).join(Relationship, Relationship.child_id == Person.id)\
                                .filter(Relationship.parent_id == person.id).all()
    parents = db.query(Person).join(Relationship, Relationship.parent_id == Person.id)\
                               .filter(Relationship.child_id == person.id).all()
    
    # Retrieve siblings by querying other children of the same parent(s) excluding the given person
    siblings = []
    for parent in parents:
        siblings.extend(db.query(Person).join(Relationship, Relationship.parent_id == parent.id)\
                                         .filter(Relationship.child_id != person.id).all())

    return {
        "person": person,
        "spouses": spouses,
        "children": children,
        "parents": parents,
        "siblings": siblings
    }



@router_person.get("/person_relationships/{person_id}", status_code=status.HTTP_200_OK)
def person_relationships(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    spouses = db.query(Person).filter(Person.id == person.spouse_id).all()
    children = db.query(Person).join(Relationship, Relationship.child_id == Person.id)\
                                .filter(Relationship.parent_id == person.id).all()
    parents = db.query(Person).join(Relationship, Relationship.parent_id == Person.id)\
                               .filter(Relationship.child_id == person.id).all()
    siblings = []
    for parent in parents:
        siblings.extend(db.query(Person).join(Relationship, Relationship.parent_id == parent.id)\
                                         .filter(Relationship.child_id != person.id).all())

    return {
        "person": person,
        "spouses": spouses,
        "children": children,
        "parents": parents,
        "siblings": siblings
    }    
    


@router_person.get("/aunts_and_uncles/{person_id}", response_model=None)
def get_aunts_and_uncles(person_id: int, db: Session = Depends(get_db)):
    # Retrieve the person from the database
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    # Retrieve the parent(s) of the person
    parent_relationships = db.query(Relationship).filter(Relationship.child_id == person_id).all()
    if not parent_relationships:
        # If person has no parent(s), return empty list
        return []

    # Extract parent IDs
    parent_ids = [relationship.parent_id for relationship in parent_relationships]

    # Query for the siblings of the parents (i.e., aunts and uncles)
    aunts_and_uncles = db.query(Person)\
        .join(Relationship, and_(Person.id == Relationship.child_id, Relationship.parent_id.in_(parent_ids)))\
        .filter(Person.id != person_id)\
        .all()

    print(aunts_and_uncles)    

    return aunts_and_uncles    


    

@router_person.post( "/create_account",status_code=status.HTTP_201_CREATED,)
def post_person(request : insert_person,db:Session=Depends(get_db),status_code=status.HTTP_201_CREATED):
    request.password=hash(request.password)
    user=Person(**request.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user    

# 
@router_person.put("/update_person/{id}",status_code=status.HTTP_202_ACCEPTED)
# ,current_user : int = Depends(get_current_user)
def update_person(id : int,request:update_person,db:Session=Depends(get_db)):
    request.password=hash(request.password)
    user=db.query(Person).filter(Person.id==id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # if user.first().id != current_user.id:
        # raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        #                     detail={"detail":"Not authorized to do suggested action"})
    user.update(dict(request),synchronize_session=False)
    db.commit()
    
@router_person.get("/persons",response_model=List[show_person],status_code=status.HTTP_302_FOUND) 
def users(db:Session=Depends(get_db)):
    users=db.query(Person).all() 
    if not users:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="No content")
    return users 

@router_person.get("/persons_registered/${user_id}",response_model=List[show_person],status_code=status.HTTP_302_FOUND) 
def users(db:Session=Depends(get_db)):
    users=db.query(Person).filter(Person.submitter==user_id).all() 
    if not users:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="No person registered")
    return users     


@router_person.get("/person/{id}",response_model=show_person,status_code=status.HTTP_302_FOUND) 
def get_order(id: int,db:Session=Depends(get_db)):
    user=db.query(Person).filter(Person.id==id).first() 
    if not user:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="No content")
    return user        


@router_person.delete("/delete_person/{id}",status_code=status.HTTP_202_ACCEPTED)
# current_user : int = Depends(get_current_user)
def delete_user(id : int,db:Session=Depends(get_db)):
    # print(current_user.id)
    user=db.query(Person).filter(Person.id==id)
    print("pass")
    if user.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"detail":f"Person id {id} does not exist"})    
    # if user.first().id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail={"detail":"Not authorized to do suggested action"})  
    user.delete(synchronize_session=False)
    db.commit() 
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# pwd | xclip -selection clipboard
# uvicorn main:app --reload =>/home/ambeyiclintone/Documents/Data-Engineering3/LegacyLines



@router_person.get("/tree_data/", status_code=status.HTTP_302_FOUND)
def get_family_data(db: Session = Depends(get_db)):

    target_person_id = 1
    
    sql_query = text(
        """
    WITH
    RankedParents AS (
        SELECT
            child.f_name AS child, parent.f_name AS parent, spouse.f_name AS spouse, ROW_NUMBER() OVER (
                PARTITION BY
                    child.id
                ORDER BY spouse.id
            ) AS row_num
        FROM
            person AS child
            LEFT JOIN relationship ON relationship.child_id = child.id
            LEFT JOIN person AS parent ON relationship.parent_id = parent.id
            LEFT JOIN person AS spouse ON child.spouse_id = spouse.id
        WHERE
            child.id = 1
            OR parent.id IS NOT NULL
            OR spouse.id IS NOT NULL
        )
        SELECT
        child,
        parent,
        CASE
        WHEN spouse IS NOT NULL THEN spouse
        END AS spouse
        FROM RankedParents
        WHERE
        row_num = 1;
        """
    )
    result = db.execute(sql_query, {"target_person_id": target_person_id}).fetchall()

    result_data = [{"child": row.child, "parent": row.parent, "spouse": row.spouse}
                   for row in result]

    modified_data = [
    {k: v for k, v in entry.items() if v is not None or k != 'spouse'}
    for entry in result_data]
             

    return modified_data


def generate_family_tree(data):
    # Plotting family tree
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_title("Family Tree")
    ax.set_xlabel("Generations")
    ax.set_ylabel("Individuals")
    def plot_individual(child, parent):
        ax.text(0, 0, child, ha='center', va='center', bbox=dict(facecolor='lightblue', alpha=0.5))
        if parent:
            ax.plot([0, 0], [0, 1], color='black')
            ax.text(0, 1, parent, ha='center', va='center', bbox=dict(facecolor='lightblue', alpha=0.5))

    for entry in data:
        plot_individual(entry['child'], entry.get('parent'))

    ax.axis('off')

    # Save the plot to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)

    # Convert the plot to base64 string
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Define FastAPI route to get family data and visualize the tree
@router_person.get("/tree_data1/", status_code=status.HTTP_200_OK)
def get_family_data(db: Session = Depends(get_db)):
    # Fetch family data from the database
    target_person_id = 2  # Assuming you have a specific target person ID
    sql_query = text(
        """
        WITH RankedParents AS (
            SELECT
                child.f_name AS child, parent.f_name AS parent, spouse.f_name AS spouse, ROW_NUMBER() OVER (
                    PARTITION BY
                        child.id
                    ORDER BY spouse.id
                ) AS row_num
            FROM
                person AS child
                LEFT JOIN relationship ON relationship.child_id = child.id
                LEFT JOIN person AS parent ON relationship.parent_id = parent.id
                LEFT JOIN person AS spouse ON child.spouse_id = spouse.id
            WHERE
                child.id = :target_person_id
                OR parent.id IS NOT NULL
                OR spouse.id IS NOT NULL
            )
            SELECT
            child,
            parent,
            CASE
            WHEN spouse IS NOT NULL THEN spouse
            END AS spouse
            FROM RankedParents
            WHERE
            row_num = 1;
        """
    )
    result = db.execute(sql_query, {"target_person_id": target_person_id}).fetchall()

    result_data = [{"child": row.child, "parent": row.parent, "spouse": row.spouse}
                   for row in result]

    modified_data = [
        {k: v for k, v in entry.items() if v is not None or k != 'spouse'}
        for entry in result_data]

    # Generate family tree plot
    img_str = generate_family_tree(modified_data)

    return {"image": img_str}











@router_person.get("/person12/{id}", status_code=status.HTTP_302_FOUND)
def get_person_details(id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == id).first()

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    # Query for children
    children = person.children

    # Query for spouse
    spouse = person.spouse

    # Query for parents
    parents = person.parents

    return {
        "person_details": {
            "id": person.id,
            "f_name": person.f_name,
            "surname": person.surname,
            "dob": person.dob,
            "home_place": person.home_place,
            "occupation": person.occupation,
            "alive": person.alive,
            "gender": person.gender,
            "email": person.email,
            "password": person.password,
            "submitter": person.submitter,
            "spouse": {
                "id": spouse.id if spouse else None,
                "f_name": spouse.f_name if spouse else None,
                "surname": spouse.surname if spouse else None,
                "dob": spouse.dob if spouse else None,
                "home_place": spouse.home_place if spouse else None,
                "occupation": spouse.occupation if spouse else None,
                "alive": spouse.alive if spouse else None,
                "gender": spouse.gender if spouse else None,
                "email": spouse.email if spouse else None,
                "password": spouse.password if spouse else None,
                "submitter": spouse.submitter if spouse else None,
            },
            "children": [{
                "id": child.id,
                "f_name": child.f_name,
                "surname": child.surname,
                "dob": child.dob,
                "home_place": child.home_place,
                "occupation": child.occupation,
                "alive": child.alive,
                "gender": child.gender,
                "email": child.email,
                "password": child.password,
                "submitter": child.submitter,
            } for child in children],
            "parents": [{
                "id": parent.id,
                "f_name": parent.f_name,
                "surname": parent.surname,
                "dob": parent.dob,
                "home_place": parent.home_place,
                "occupation": parent.occupation,
                "alive": parent.alive,
                "gender": parent.gender,
                "email": parent.email,
                "password": parent.password,
                "submitter": parent.submitter,
            } for parent in parents],
        }
    }



def generate_pdf_report(users):
    doc = SimpleDocTemplate("users_report.pdf", pagesize=letter)
    elements = []

    data = [["ID", "First Name", "Last Name", "Occupation", "Parents", "Children", "Spouse"]]
    for user in users:
        parent_names = ", ".join([parent.f_name for parent in user.parents])
        children_names = ", ".join([child.f_name for child in user.children])
        spouse_name = user.spouse.f_name if user.spouse else ""

        data.append([
            str(user.id),
            user.f_name,
            user.surname,
            user.occupation,
            parent_names,
            children_names,
            spouse_name
        ])

    # Create a table
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    elements.append(table)
    doc.build(elements)
    return "users_report.pdf"




@router_person.get("/generate_report", response_class=Response, tags=["Reports"])
async def generate_report(db: Session = Depends(get_db)):
    try:
        # Retrieve all users from the database
        users = db.query(Person).all()
        # db.close()

        # Generate PDF report
        pdf_path = generate_pdf_report(users)

        # Return the generated PDF as a downloadable response
        with open(pdf_path, "rb") as file:
            pdf_content = file.read()

        return Response(content=pdf_content, media_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=users_report.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))