from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return render_template("logout.html")

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        check_register_info(request)

    return render_template("register.html")


def check_register_info(request):
    email = request.form.get('email')
    user_name = request.form.get('user_name')
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirmation')

    if len(email) < 6:
        flash('Email must have at least 5 characters.', category='error')
    elif len(user_name) < 2:
        flash('User name must have at least 2 characters.', category='error')
    elif password != password_confirmation:
        flash('Passwords don\'t match', category='error')
    elif len(password) < 7:
        flash('Passwords must have atleast 6 characters', category='error')
    else: 
        flash('Account created!', category='success')
        pass 