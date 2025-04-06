import pytest
from app import app
from models import db, Employee

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add test data
            emp1 = Employee(name="John Doe", salary=50000)
            emp2 = Employee(name="Jane Smith", salary=60000)
            db.session.add_all([emp1, emp2])
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_get_employees(client):
    # Test getting all employees
    response = client.get('/employees')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['name'] == "John Doe"
    assert data[1]['name'] == "Jane Smith"
    
    # Test department filtering
    response = client.get('/employees?department=IT')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 0  # No employees in IT department initially

def test_email_validation(client):
    # Test invalid email
    response = client.post('/employees', json={
        'name': 'Test',
        'email': 'invalid-email'
    })
    assert response.status_code == 400
    assert 'Invalid email format' in response.get_json()['error']

    # Test missing email
    response = client.post('/employees', json={
        'name': 'Test'
    })
    assert response.status_code == 400
    assert 'Email is required' in response.get_json()['error']

def test_create_employee(client):
    new_emp = {
        'name': 'New Employee',
        'email': 'new@example.com',
        'salary': 70000,
        'department': 'HR'
    }
    response = client.post('/employees', json=new_emp)
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'New Employee'
    assert data['email'] == 'new@example.com'
    assert data['salary'] == 70000
    assert data['department'] == 'HR'
    assert 'hire_date' in data

def test_get_single_employee(client):
    response = client.get('/employees/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "John Doe"
    assert 'email' in data
    assert 'department' in data
    assert 'hire_date' in data

def test_update_employee(client):
    update_data = {'name': 'Updated Name', 'salary': 55000}
    response = client.patch('/employees/1', json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Updated Name'
    assert data['salary'] == 55000

def test_delete_employee(client):
    response = client.delete('/employees/1')
    assert response.status_code == 200
    response = client.get('/employees/1')
    assert response.status_code == 404
