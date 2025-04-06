from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# contains definitions of tables and associated schema constructs
metadata = MetaData()

# create the Flask SQLAlchemy extension
db = SQLAlchemy(metadata=metadata)

# define a model class by inheriting from db.Model.


class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    salary = db.Column(db.Integer)
    department = db.Column(db.String)
    hire_date = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Employee {self.id}, {self.name}, {self.email}, {self.department}>'
