from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .terraform_scripts.terraform_utils import launch_aws_instance, terminate_aws_instance
from .models import Instance, db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == "POST":
        instance_type = request.form.get('selectedOptionInstanceType')
        private_ssh_key = launch_aws_instance(instance_type)
        return render_template('connection.html', user=current_user, private_ssh_key=private_ssh_key)
    return render_template('home.html', user=current_user)

@views.route('/instance_details', methods=['GET', 'POST'])
@login_required
def instance_details():
   def get_instances_by_user():
            instances_by_user = Instance.query.filter_by(user_id=current_user.id).all()
            instance_aws_ids = [instance.aws_instance_id for instance in instances_by_user]
            return instance_aws_ids

   if request.method == "POST":
        server_id = request.form.get('server_id')
        terminate_aws_instance(server_id)

        instances = get_instances_by_user()
        return render_template('instances.html', user=current_user, instance_aws_ids=instances)

   instances = get_instances_by_user()
   return render_template('instances.html', user=current_user, instance_aws_ids=instances)