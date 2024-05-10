from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .terraform_scripts.terraform_utils import launch_aws_instance

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == "POST":
        instance_type = request.form.get('selectedOptionInstanceType')
        private_ssh_key = launch_aws_instance(instance_type)
        return render_template('connection.html', user=current_user, private_ssh_key=private_ssh_key)
    return render_template('home.html', user=current_user)