# server/app.py

import re
from datetime import datetime
from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate

from models import db, Employee

# create a Flask application instance 
app = Flask(__name__)

# configure the database connection to the local file app.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create a Migrate object to manage schema modifications
migrate = Migrate(app, db)

# initialize the Flask application to use the database
db.init_app(app)

@app.route('/employees', methods=['GET'])
def get_employees():
    department = request.args.get('department')
    if department:
        employees = Employee.query.filter_by(department=department).all()
    else:
        employees = Employee.query.all()
    return jsonify([{
        'id': emp.id,
        'name': emp.name,
        'email': emp.email,
        'salary': emp.salary,
        'department': emp.department,
        'hire_date': emp.hire_date.isoformat() if emp.hire_date else None
    } for emp in employees])

@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    if not data or 'name' not in data:
        return make_response(jsonify({'error': 'Name is required'}), 400)
    
    if not data.get('email'):
        return make_response(jsonify({'error': 'Email is required'}), 400)
    
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', data['email']):
        return make_response(jsonify({'error': 'Invalid email format'}), 400)
    
    employee = Employee(
        name=data['name'],
        email=data['email'],
        salary=data.get('salary'),
        department=data.get('department'),
        hire_date=datetime.utcnow()
    )
    db.session.add(employee)
    db.session.commit()
    return jsonify({
        'id': employee.id,
        'name': employee.name,
        'email': employee.email,
        'salary': employee.salary,
        'department': employee.department,
        'hire_date': employee.hire_date.isoformat() if employee.hire_date else None
    }), 201

@app.route('/employees/<int:id>', methods=['GET'])
def get_employee(id):
    employee = Employee.query.get(id)
    if not employee:
        return make_response(jsonify({'error': 'Employee not found'}), 404)
    return jsonify({
        'id': employee.id,
        'name': employee.name,
        'email': employee.email,
        'salary': employee.salary,
        'department': employee.department,
        'hire_date': employee.hire_date.isoformat() if employee.hire_date else None
    })

@app.route('/employees/<int:id>', methods=['PATCH'])
def update_employee(id):
    employee = Employee.query.get(id)
    if not employee:
        return make_response(jsonify({'error': 'Employee not found'}), 404)
    
    data = request.get_json()
    if 'name' in data:
        employee.name = data['name']
    if 'salary' in data:
        employee.salary = data['salary']
    
    db.session.commit()
    return jsonify({
        'id': employee.id,
        'name': employee.name,
        'salary': employee.salary
    })

@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    employee = Employee.query.get(id)
    if not employee:
        return make_response(jsonify({'error': 'Employee not found'}), 404)
    
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Employee deleted'})

if __name__ == '__main__':
    app.run(port=5555, debug=True)
