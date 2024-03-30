from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from .utils import Base
from sqlalchemy.sql import func
from sqlalchemy.types import Time

class Person(Base):
    __tablename__ = "person"
    id = Column(Integer, primary_key=True, index=True)
    f_name = Column(String(256), nullable=True)
    surname = Column(String(256), nullable=True)
    dob = Column(Date, nullable=True)
    home_place = Column(String(256), nullable=True)
    occupation = Column(String(50), nullable=False)
    alive = Column(Boolean, nullable=True)
    gender = Column(String(25), nullable=False)
    email = Column(String(256), index=True, nullable=True)
    password = Column(String(256), nullable=True)
    submitter=Column(Integer,nullable=True)

    # Relationship with spouse
    spouse_id = Column(Integer, ForeignKey('person.id'))
    spouse = relationship('Person', remote_side=[id], backref='spouses')

    # Relationships with children and parents
    parent_relationships = relationship('Relationship', foreign_keys='Relationship.parent_id', back_populates='parent')
    children_relationships = relationship('Relationship', foreign_keys='Relationship.child_id', back_populates='child')

    @property
    def parents(self):
        return [rel.parent for rel in self.parent_relationships]

    @property
    def children(self):
        return [rel.child for rel in self.children_relationships]

class Relationship(Base):
    __tablename__ = "relationship"
    rel_id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("person.id", onupdate="CASCADE"))
    child_id = Column(Integer, ForeignKey("person.id", onupdate="CASCADE"))

    parent = relationship("Person", back_populates="parent_relationships", foreign_keys=[parent_id])
    child = relationship("Person", back_populates="children_relationships", foreign_keys=[child_id])

class Events(Base):  
    __tablename__ = "events"  
    event_id=Column(Integer, primary_key=True, index=True)
    f_name = Column(String(256), nullable=True)
    surname = Column(String(256), nullable=True)
    host_title = Column(String(256), nullable=True)
    event_title = Column(String(256), nullable=True)
    venue = Column(String(256), nullable=True)
    event_date = Column(Date, nullable=True)
    event_time = Column(Time, nullable=True)
    description=Column(String(500),nullable=True)
    created_by = Column(Integer,ForeignKey("person.id", onupdate="CASCADE"))
    created_at = Column(Date,nullable=True)


