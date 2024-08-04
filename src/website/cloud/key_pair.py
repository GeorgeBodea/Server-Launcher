from datetime import datetime
from uuid import uuid4
from flask_login import current_user

class KeyPairManager:
    def __init__(self, ec2_client):
        self.ec2_client = ec2_client

    def process_key_pair(self):
        """
        Creates an SSH key pair for the current user and returns the key name and private key material.

        Returns:
            tuple: A tuple containing the key name and the private key material.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        unique_id = str(uuid4())
        key_name = f"ssh_key_{current_user.user_name}_{unique_id}_{timestamp}"
        
        try:
            response = self.ec2_client.create_key_pair(KeyName=key_name)
            return key_name, response['KeyMaterial']
        except self.ec2_client.exceptions.ClientError as e:
            print(f"Error creating key pair: {e}")
            return None, None
