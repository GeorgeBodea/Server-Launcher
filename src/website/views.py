from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from .cloud.aws_utils import AWSUtilsManager

class ViewController:
    views = Blueprint('views', __name__)
    aws_utils = AWSUtilsManager()

    @staticmethod
    def extract_tool_selections(form_data):
        tool_selections = []
        tool_versions = {}
        component_count = len([key for key in form_data.keys() if 'selectedOptionTool' in key])

        for i in range(component_count):
            tool = form_data.get(f'selectedOptionTool{i}')
            version = form_data.get(f'selectedOptionVersion{i}')
            if tool and version:
                if tool in tool_versions:
                    tool_versions[tool].append(version)
                else:
                    tool_versions[tool] = [version]
    
        single_version_tools = ['MySQL', 'MariaDB']  # Add other single-version tools here
        for tool in single_version_tools:
            if tool in tool_versions and len(tool_versions[tool]) > 1:
                flash(f"Multiple versions selected for {tool}. Only one version is recommended.", category="error")
                return []  # Return an empty list to indicate an error

        
        return tool_selections

    @views.route('/', methods=['GET', 'POST'])
    @login_required
    def home():
        if request.method == "POST":
            instance_type = request.form.get('selectedOptionInstanceType')
            image_id = request.form.get('selectedOptionAmiType')
            tool_selections = ViewController.extract_tool_selections(request.form)

            root_user = ViewController.aws_utils.get_root_user(image_id)          

            if not instance_type:
                flash("Please select an instance type.", category="error")
            elif not image_id:
                flash("Please select an AMI type.", category="error")
            else:
                user_data_script = render_template('user_data_setup/user_data.sh.j2', tool_selections=tool_selections)

                instance_id, private_ssh_key, public_ip, public_dns = ViewController.aws_utils.launch_instance(image_id, instance_type)
                return render_template('connection.html',
                                    user=current_user,
                                    aws_instance_id=instance_id,
                                    private_ssh_key=private_ssh_key,
                                    public_ip=public_ip,
                                    public_dns=public_dns,
                                    root=root_user)
        
        return render_template('home.html', user=current_user)

    @views.route('/launch_game_server', methods=['GET', 'POST'])
    @login_required
    def launch_game_server():
        if request.method == "POST":
            game = request.form.get('selectedGame')

            if not game:
                flash("Please select a game server type.", category="error")
            else:
                image_id, instance_type = ViewController.aws_utils.get_server_details(game)
                root_user = ViewController.aws_utils.get_root_user(image_id)

                instance_id, private_ssh_key, public_ip, public_dns = ViewController.aws_utils.launch_instance(image_id, instance_type)
                return render_template('connection.html',
                                       user=current_user,
                                       aws_instance_id=instance_id,
                                       private_ssh_key=private_ssh_key,
                                       public_ip=public_ip,
                                       public_dns=public_dns,
                                       root_user=root_user)
        
        return render_template('game_servers.html', user=current_user)

    @views.route('/instance_details', methods=['GET', 'POST'])
    @login_required
    def instance_details():
        if request.method == "POST":
            server_id = request.form.get('server_id')
            ViewController.aws_utils.terminate_instance(server_id)

            # After termination, update the instance detail page
            instances_info = ViewController.aws_utils.list_instances()
            return render_template('instances.html', user=current_user, instances_info=instances_info)

        instances_info = ViewController.aws_utils.list_instances()
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
