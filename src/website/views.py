from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from .cloud.aws_utils import launch_aws_instance, terminate_aws_instance, get_instances_info, choose_root

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == "POST":
        instance_type = request.form.get('selectedOptionInstanceType')
        image_id = request.form.get('selectedOptionAmiType')
        root_user = choose_root(image_id)

        if not instance_type:
            flash("Please select an instance type.", category="error")
        elif not image_id:
            flash("Please select an AMI type.", category="error")
        else:
            instance_id, private_ssh_key, public_ip, public_dns = launch_aws_instance(image_id, instance_type)
            return render_template('connection.html', user=current_user, 
                                aws_instance_id=instance_id, 
                                private_ssh_key=private_ssh_key,
                                public_ip=public_ip,
                                public_dns=public_dns,
                                root=root_user)
        
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

@views.route('/download_key', methods=['POST'])
@login_required
def download_key():
    private_key = request.form.get('private_key')
    if private_key:
        return Response(
            private_key,
            mimetype='text/plain',
            headers={'Content-Disposition': 'attachment;filename=private_key.pem'}
        )
    else:
        flash('Private key not found', category='error')
        return redirect(url_for('views.home'))