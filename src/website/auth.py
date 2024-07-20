from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password') 

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Successfully logged in!', category='success')

                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password.', category='error')
        else:
            flash('Email does not exists.', category='error')
    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        isRegistered = check_and_register(request)
        if isRegistered: 
            return redirect(url_for('views.home'))

    return render_template('register.html', user=current_user)


def check_and_register(request):
    email = request.form.get('email')
    user_name = request.form.get('user_name')
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirmation')

    user_by_email = User.query.filter_by(email=email).first()
    user_by_name = User.query.filter_by(user_name=user_name).first()
    if user_by_email:
        flash('Email already exists!', category='error')
    elif user_by_name:
        flash('User name already exists!', category='error')
    elif len(email) < 6:
        flash('Email must have at least 5 characters.', category='error')
    elif len(user_name) < 2:
        flash('User name must have at least 2 characters.', category='error')
    elif password != password_confirmation:
        flash('Passwords don\'t match', category='error')
    elif len(password) < 7:
        flash('Passwords must have atleast 6 characters', category='error')
    else: 
        new_user = User(email=email, user_name=user_name, password=generate_password_hash(password))

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user, remember=True)

        flash('Account created!', category='success')
        return True
    
    return False