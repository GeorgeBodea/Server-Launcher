from datetime import datetime
from uuid import uuid4
from flask_login import current_user

def process_key_pair(ec2_client):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    unique_id = str(uuid4())
    key_name = f"ssh_key_{current_user.user_name}_{unique_id}_{timestamp}"
    response = ec2_client.create_key_pair(KeyName=key_name)
    return key_name, response['KeyMaterial']