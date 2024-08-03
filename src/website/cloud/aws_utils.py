from boto3 import Session
from .key_pair import process_key_pair
from .instance_management import launch_aws_instance, terminate_aws_instance, get_instances_info
from .security_group import create_security_group, get_security_group_id_for_user
from .utils import choose_root, get_game_server_details

# AWS connection objects
aws_session = Session(profile_name='default')
ec2_client = aws_session.client('ec2')

# Key Pair Operations
def create_key_pair():
    return process_key_pair(ec2_client)

# Instance Management
def launch_instance(image_id, instance_type):
    return launch_aws_instance(ec2_client, image_id, instance_type, create_key_pair, get_security_group_id, create_security_group_for_user)

def terminate_instance(server_id):
    return terminate_aws_instance(ec2_client, server_id)

def list_instances():
    return get_instances_info(ec2_client)

# Security Group Management
def create_security_group_for_user(user_id, user_email):
    return create_security_group(ec2_client, user_id, user_email)

def get_security_group_id(user_id, user_email):
    return get_security_group_id_for_user(ec2_client, user_id, user_email)

# Utility Functions
def get_root_user(image_id):
    return choose_root(image_id)

def get_server_details(game):
    return get_game_server_details(game)