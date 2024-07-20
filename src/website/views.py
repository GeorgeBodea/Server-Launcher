from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .cloud.aws_utils import launch_aws_instance, terminate_aws_instance, get_instances_info

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
   if request.method == "POST":
        server_id = request.form.get('server_id')
        terminate_aws_instance(server_id)

        # After termination, one instance is deteled and information on the instance detail page must be updated
        instances_info = get_instances_info()
        return render_template('instances.html', user=current_user, instances_info=instances_info)

   instances_info = get_instances_info()
   return render_template('instances.html', user=current_user, instances_info=instances_info)