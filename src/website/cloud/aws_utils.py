from boto3 import Session
from .key_pair import KeyPairManager
from .instance_management import InstanceManager
from .security_group import SecurityGroupManager
from .utils import Utils
from .user_data import UserDataManager

class AWSUtilsManager:
    def __init__(self):
        self.aws_session = Session(profile_name='default')
        self.ec2_client = self.aws_session.client('ec2')
        self.key_pair_manager = KeyPairManager(self.ec2_client)
        self.instance_manager = InstanceManager(self.ec2_client)
        self.security_group_manager = SecurityGroupManager(self.ec2_client)
        self.user_data_manager = UserDataManager() 

    def create_key_pair(self):
        """
        Creates a key pair using the KeyPairManager.

        Returns:
            tuple: A tuple containing the key name and the private key material.
        """
        return self.key_pair_manager.process_key_pair()

    def launch_instance(self, image_id, instance_type, tool_selections):
        """
        Launches an EC2 instance with the specified parameters.

        Parameters:
            image_id (str): The ID of the AMI.
            instance_type (str): The type of instance to launch.
            tool_selections (list): The selected tools and versions.

        Returns:
            tuple: A tuple containing instance ID, private key, public IP, and public DNS.
        """
        # Generate the User Data script based on the tool selections
        user_data_script = self.user_data_manager.generate_user_data_script(tool_selections)

        return self.instance_manager.launch_aws_instance(
            image_id,
            instance_type,
            self.create_key_pair,
            self.get_security_group_id,
            self.create_security_group_for_user,
            user_data_script=user_data_script 
        )

    def terminate_instance(self, server_id):
        """
        Terminates the specified EC2 instance.

        Parameters:
            server_id (str): The ID of the instance to terminate.
        """
        return self.instance_manager.terminate_aws_instance(server_id)

    def list_instances(self):
        """
        Lists all instances for the current user.

        Returns:
            list: A list of tuples containing instance details.
        """
        return self.instance_manager.get_instances_info()

    def create_security_group_for_user(self, user_id, user_email):
        """
        Creates a security group for the specified user.

        Parameters:
            user_id (int): The ID of the user.
            user_email (str): The email of the user.

        Returns:
            str: The ID of the created security group.
        """
        return self.security_group_manager.create_security_group(user_id, user_email)

    def get_security_group_id(self, user_id, user_email):
        """
        Retrieves the security group ID for the specified user.

        Parameters:
            user_id (int): The ID of the user.
            user_email (str): The email of the user.

        Returns:
            str: The ID of the security group, or None if not found.
        """
        return self.security_group_manager.get_security_group_id_for_user(user_id, user_email)

    def get_root_user(self, image_id):
        """
        Retrieves the root user for a given AMI ID.

        Parameters:
            image_id (str): The ID of the AMI.

        Returns:
            str: The root user for the specified AMI.
        """
        return Utils.choose_root(image_id)

    def get_server_details(self, game):
        """
        Retrieves the AMI ID and instance type for a specified game server.

        Parameters:
            game (str): The identifier for the game server.

        Returns:
            tuple: A tuple containing the AMI ID and instance type.
        """
        return Utils.get_game_server_details(game)
