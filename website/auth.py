# authentication routes: this file handles login, logout, signup

from datetime import datetime
from flask import Blueprint, request, flash, redirect, url_for, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_user, login_required, logout_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember = True)
                if user.role == 'manager':
                    flash('Logged in successfully!', category = 'success')
                    return redirect(url_for('views.manager_dashboard'))
                else:
                    flash('Logged in successfully!', category = 'success')
                    return redirect(url_for('views.employee_dashboard'))
            else:
                flash('Login failed. Check email and password', category= 'error')
        else:
            flash('Email does not exist.', category='error')

        #hardcoded for login
        #if email == 'ad@gmail.com' and password == '1234':
            #flash('Logged in successfully!', category = 'success')
            #return redirect(url_for('views.home'))
        #else:
            #flash('Login failed', category = 'error')
    return render_template('login.html', user = current_user)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# @auth.route('/sign-up', methods = ['GET', 'POST'])
# def sign_up():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         first_name = request.form.get('firstName')
#         password1 = request.form.get('password1')
#         password2 = request.form.get('password2')
#         role = request.form.get('role')

#         user = User.query.filter_by(email=email).first()
#         if user:
#             flash('Email already exists.', category='error')
#         elif password1 != password2:
#             flash('Passwords do not match.', category='error')
#         else:
#             new_user = User(
#                 email=email,
#                 first_name=first_name,
#                 password=generate_password_hash(password1),
#                 role=role
#             )
#             db.session.add(new_user)
#             db.session.commit()
#             login_user(new_user, remember=True)
#             flash('Account created!', category='success')
#             return redirect(url_for('views.home'))

#     return render_template('sign_up.html', user = current_user)

@auth.route('/sign-up/employee', methods = ['GET', 'POST'])
def sign_up_employee():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        date_of_birth = request.form.get('date_of_birth')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(first_name) <= 1 or len(last_name) <= 1:
            flash('First and last name must be longer than 1 character.', category='error')
        elif len(password1) < 4:
            flash('Password must be at least 4 characters long.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif "@admin.com" in email:
            flash('Employees cannot use @admin.com email.', category='error')
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                last_name = last_name,
                phone_number = phone_number,
                address = address,
                date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d'),
                password=generate_password_hash(password1),
                role="employee"
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Employee account created!', category='success')
            return redirect(url_for('views.home'))
    return render_template('sign_up_employee.html', user=current_user)

@auth.route('/sign-up/manager', methods = ['GET', 'POST'])
def sign_up_manager():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(first_name) <= 1 or len(last_name) <= 1:
            flash('First and last name must be longer than 1 character.', category='error')
        elif len(password1) < 4:
            flash('Password must be at least 4 characters long.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif not email.endswith("@admin.com"):
            flash('Managers must use an @admin.com email.', category='error')
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                last_name = last_name,
                password=generate_password_hash(password1),
                role="manager"
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Manager account created!', category='success')
            return redirect(url_for('views.home'))
    return render_template('sign_up_manager.html', user=current_user)
    