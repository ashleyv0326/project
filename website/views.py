#application views: dashboard, core functionalities for managers / employees

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from website.models import User, Workhours, Project
from . import db
from sqlalchemy import func 
# blueprint of the application

views = Blueprint('views', __name__)

#set up blueprint for flask
#home page 
@views.route('/', methods = ['GET', 'POST'])
def home():
    #return "<h1>Test</h1>"
    return render_template('home.html', user = current_user)
    #if current_user.role == 'manager':
    #     return redirect(url_for('views.manager_dashboard'))
    #return redirect(url_for('views.employee_dashboard'))

# manager dashboard (i.e: manager homepage)
@views.route('/manager', methods = ['GET', 'POST'])
@login_required
def manager_dashboard():
    # if current_user.role != 'manager':
    #     return redirect(url_for('views.manager_dashboard'))
    # return render_template('manager_dashboard.html')
    if current_user.role != 'manager':
        return redirect(url_for('auth.login'))
    
    # Fetch all employees and their total hours logged per project
    employees_hours = db.session.query(
        User.id.label('employee_id'), User.first_name, User.last_name,
        Project.name.label('project'),
        func.sum(Workhours.hours).label('total_hours')
    ).join(Workhours, Workhours.user_id == User.id, isouter = True) \
     .join(Project, Workhours.project_id == Project.id, isouter = True) \
     .filter(User.role == 'employee') \
     .group_by(User.id, Project.name)\
     .all()
    
    # Fetch all employees
    employees_list = User.query.filter(User.role == 'employee').all()
    #fetch all existing project
    projects = Project.query.all()
    
    return render_template('manager_dashboard.html', user = current_user, employees=employees_hours, employees_list = employees_list, projects=projects)

# manager adding project 
@views.route('/manager/add_project', methods=['POST'])
@login_required
def add_project():
    if current_user.role != 'manager':
        return redirect(url_for('auth.login'))
    
    project_name = request.form.get('project_name')
    if project_name:
        existing_project = Project.query.filter_by(name=project_name).first()
        if not existing_project:
            new_project = Project(name=project_name)
            db.session.add(new_project)
            db.session.commit()
            flash('Project added successfully!', category='success')
        else:
            flash('Project already exists.', category='error')
    return redirect(url_for('views.manager_dashboard'))

@views.route('/manager/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    if current_user.role != 'manager':
        return redirect(url_for('auth.login'))
    
    project = Project.query.get(project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully!', category='success')
    else:
        flash('Project not found.', category='error')
    return redirect(url_for('views.manager_dashboard'))

@views.route('/manager/assign_project', methods=['POST'])
@login_required
def assign_project():
    if current_user.role != 'manager':
        return redirect(url_for('auth.login'))
    
    employee_id = request.form.get('employee_id')
    project_id = request.form.get('project_id')
    
    # Check if the employee and project exist
    employee = User.query.get(employee_id)
    project = Project.query.get(project_id)
    
    if not employee or not project:
        flash('Invalid employee or project selection.', category='error')
    elif employee.role != 'employee':
        flash('Cannot assign projects to non-employees.', category='error')
    else:
        # Assign the project to the employee
        workhours = Workhours.query.filter_by(user_id=employee.id, project_id=project.id).first()
        if not workhours:
            new_workhours = Workhours(user_id=employee.id, project_id=project.id, hours=0)
            db.session.add(new_workhours)
            db.session.commit()
            flash(f'Assigned project "{project.name}" to {employee.first_name} {employee.last_name}.', category='success')
        else:
            flash(f'{employee.first_name} {employee.last_name} is already assigned to "{project.name}".', category='info')

    return redirect(url_for('views.manager_dashboard'))

@views.route('/manager/report', methods=['GET'])
@login_required
def manager_report():
    if current_user.role != 'manager':
        return redirect(url_for('auth.login'))
    
    projects = Project.query.all()
    report = []
    for project in projects:
        total_hours = db.session.query(db.func.sum(Workhours.hours)).filter_by(project_id=project.id).scalar() or 0
        #fetch employees & their hours for this project
        employees = Workhours.query.filter_by(project_id=project.id).all()
        employee_details = []
        for emp in employees:
            if emp.employee:  # Ensure the employee relationship exists
                employee_details.append({
                    'id': emp.employee.id,
                    'name': f'{emp.employee.first_name} {emp.employee.last_name}',
                    'hours': emp.hours
                })
        report.append({
            'project': project.name,
            'total_hours': total_hours,
            'employee_details': employee_details
        })
    return render_template('manager_report.html', report=report)


@views.route('/employee', methods = ['GET', 'POST'])
@login_required
def employee_dashboard():
    if current_user.role != 'employee':
        return redirect(url_for('auth.login'))
    # Fetch projects assigned to the logged-in employee
    assigned_projects = db.session.query(Project).join(Workhours).filter(Workhours.user_id == current_user.id).all()
    return render_template('employee_dashboard.html', user=current_user, projects=assigned_projects)

@views.route('/employee/update', methods=['GET', 'POST'])
@login_required
def update_employee_info():
    if current_user.role != 'employee':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        date_of_birth = request.form.get('date_of_birth')

        # Update current user info
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.phone_number = phone_number
        current_user.address = address
        current_user.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d')
        db.session.commit()
        flash('Information updated successfully!', category='success')
        return redirect(url_for('views.employee_dashboard'))

    return render_template('update_employee_info.html', user=current_user)

@views.route('/employee/log_hours', methods=['POST'])
@login_required
def log_hours():
    if current_user.role != 'employee':
        return redirect(url_for('auth.login'))
    
    project_id = request.form.get('project_id')
    hours = float(request.form.get('hours', 0))
    
    if not project_id or not hours or float(hours) <= 0:
        flash('Invalid hours or project selection.', category = 'error')
        return redirect(url_for('views.employee_dashboard'))
    
    workhours = Workhours.query.filter_by(user_id=current_user.id, project_id=project_id).first()
    #db.session.add(workhours)
    if workhours:
        workhours.hours += hours  # Update hours
    else:
        flash('You are not assigned to this project.', category='error')
        return redirect(url_for('views.employee_dashboard'))
    
    db.session.commit()
    flash('Hours registered successfully!', category= 'success')
    return redirect(url_for('views.employee_dashboard'))