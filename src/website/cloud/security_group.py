from botocore.exceptions import ClientError

def create_security_group(ec2_client, user_id, user_email):
    sg_name = f"sg_{user_id}_{user_email}"
    try:
        response = ec2_client.create_security_group(
            GroupName=sg_name,
            Description=f"Security group created for {user_email}"
        )
        security_group_id = response['GroupId']

        ec2_client.authorize_security_group_ingress(
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

def get_security_group_id_for_user(ec2_client, user_id, user_email):
    sg_name = f"sg_{user_id}_{user_email}"
    try:
        response = ec2_client.describe_security_groups(
            Filters=[{'Name': 'group-name', 'Values': [sg_name]}]
        )
        if response['SecurityGroups']:
            return response['SecurityGroups'][0]['GroupId']
        return None
    except ClientError as e:
        print(f"Error retrieving security group: {e}")
        return None