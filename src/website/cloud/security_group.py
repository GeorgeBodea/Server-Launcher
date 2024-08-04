from botocore.exceptions import ClientError

class SecurityGroupManager:
    def __init__(self, ec2_client):
        self.ec2_client = ec2_client

    def create_security_group(self, user_id, user_email):
        """
        Creates a security group for the specified user.

        Parameters:
            user_id (int): The ID of the user.
            user_email (str): The email of the user.

        Returns:
            str: The ID of the created security group, or None if creation failed.
        """
        sg_name = f"sg_{user_id}_{user_email}"
        try:
            response = self.ec2_client.create_security_group(
                GroupName=sg_name,
                Description=f"Security group created for {user_email}"
            )
            security_group_id = response['GroupId']

            self.ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                    {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                    {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
                ]
            )

            return security_group_id
        except ClientError as e:
            print(f"Error creating security group: {e}")
            return None

    def get_security_group_id_for_user(self, user_id, user_email):
        """
        Retrieves the security group ID for the specified user.

        Parameters:
            user_id (int): The ID of the user.
            user_email (str): The email of the user.

        Returns:
            str: The ID of the security group, or None if not found.
        """
        sg_name = f"sg_{user_id}_{user_email}"
        try:
            response = self.ec2_client.describe_security_groups(
                Filters=[{'Name': 'group-name', 'Values': [sg_name]}]
            )
            if response['SecurityGroups']:
                return response['SecurityGroups'][0]['GroupId']
            return None
        except ClientError as e:
            print(f"Error retrieving security group: {e}")
            return None
