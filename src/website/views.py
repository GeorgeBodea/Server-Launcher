from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .terraform_scripts.terraform_utils import launch_aws_instance

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == "POST":
        instance_type = request.form.get('selectedOptionInstanceType')
        launch_aws_instance(instance_type)
    return render_template("home.html", user=current_user)