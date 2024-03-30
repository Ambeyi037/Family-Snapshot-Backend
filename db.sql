INSERT INTO
    person (
        f_name, surname, dob, place_of_birth, alive, gender, email, marital_status, password, spouse_id
    )
VALUES (
        "Washingtone", "Mutende", "1972-01-01", "Butere", true, "male", "mutende@gmail.com", true, "mutende", NULL
    ),
    (
        "Judith", "Misiko", "1981-01-01", "Mumias", true, "female", "misiko@gmail.com", true, "misiko", NULL
    ),
    (
        "Clintone", "Ambeyi", "2001-01-01", "Butere", true, "male", "ambeyi@gmail.com", false, "ambeyi", NULL
    ),
    (
        "Purity", "Alunya", "2003-01-01", "Butere", true, "female", "alunya@gmail.com", false, "alunya", NULL
    ),
    (
        "Isaac", "Mutende", "2007-01-01", "Butere", true, "male", "isaac@gmail.com", false, "isaac", NULL
    );

INSERT INTO
    person (
        f_name, surname, dob, place_of_birth, alive, gender, email, marital_status, password, spouse_id
    )
VALUES (
        'John', 'Doe', '1990-01-01', 'City1', true, 'Male', 'john.doe@example.com', false, 'hashed_password_1', NULL
    );

-- Query child,parent and the child spouse
from
    sqlalchemy.orm import aliased
    # Assuming you have a session object
    session = Session ()
    # Specify the target person ID
    target_person_id = 1
    # Aliases for the person table to represent child, parent, and spouse
    Child = aliased (Person) Parent = aliased (Person) Spouse = aliased (Person)

result = (
    session.query(
        Child.f_name.label('child'),
        Parent.f_name.label('parent'),
        case([(Spouse.f_name.isnot(None), Spouse.f_name)], else_=None).label('spouse')
    )
    .filter(Child.id == target_person_id)
    .outerjoin(Relationship, Relationship.child_id == Child.id)
    .outerjoin(Parent, Relationship.parent_id == Parent.id)
    .outerjoin(Spouse, Child.spouse_id == Spouse.id)
    .filter(
        (Parent.id == Child.parent_id) |
        (Parent.id == None)
    )
    .all()
)

# Access the result as a list of dictionaries
result_data = [
    {"child": row.child, "parent": row.parent, "spouse": row.spouse}
    for row in result
]

# Close the session
session.close ()
-- SQL version