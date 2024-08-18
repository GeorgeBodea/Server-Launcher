from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_login import login_required, current_user
from .cloud.aws_utils import AWSUtilsManager

class ViewController:
    views = Blueprint('views', __name__)
    aws_utils = AWSUtilsManager()

    @staticmethod
    def extract_tool_selections(form_data):
        tool_versions_dict = dict()
        component_count = len([key for key in form_data.keys() if key.startswith('selectedOptionTool')])

        for i in range(component_count):
            tool = form_data.get(f'selectedOptionTool{i}')
            version = form_data.get(f'selectedOptionVersion{i}')

            if tool and version:
                if tool in tool_versions_dict:
                    tool_versions_dict[tool].append(version)
                else:
                    tool_versions_dict[tool] = [version]
    
        single_version_tools = ['MySQL', 'MariaDB']
        for tool in single_version_tools:
            if tool in tool_versions_dict and len(tool_versions_dict[tool]) > 1:

                flash(f"Multiple versions selected for {tool}. Only one version is recommended.", category="error")
                return [] 

        return tool_versions_dict

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

                instance_id, private_ssh_key, public_ip, public_dns = ViewController.aws_utils.launch_instance(image_id, instance_type, tool_selections)
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
                instance_id, private_ssh_key, public_ip, public_dns = ViewController.aws_utils.launch_instance(image_id, instance_type, tool_selections=[])
                
                return render_template('connection.html',
                                       user=current_user,
                                       aws_instance_id=instance_id,
                                       private_ssh_key=private_ssh_key,
                                       public_ip=public_ip,
                                       public_dns=public_dns,
                                       root=root_user)
        
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

    @views.route('/toggle_instance', methods=['POST'])
    def toggle_instance():
        data = request.json
        server_id = data.get('server_id')
        action = data.get('action')

        if action == 'stop':
            success = ViewController.aws_utils.stop_instance(server_id)
        elif action == 'start':
            success = ViewController.aws_utils.start_instance(server_id)
        else:
            success = False

        return jsonify({'success': success})

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
