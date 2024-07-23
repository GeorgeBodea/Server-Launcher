
from pathlib import Path
from flask_login import current_user
from flask import flash
from boto3 import Session, resource
from botocore.exceptions import ClientError
from datetime import datetime
from uuid import uuid4
from time import sleep

current_folder = Path(__file__).parent.absolute()

# Terraform scripts paths
aws_instance_script = current_folder / 'aws_instance.tf' 

# AWS connection objects
aws_session = Session(profile_name='default')
ec2_client = aws_session.client('ec2')

def process_key_pair():
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    unique_id = str(uuid4())
    key_name = f"ssh_key_{current_user.user_name}_{unique_id}_{timestamp}" 
    response = ec2_client.create_key_pair(KeyName=key_name)
    return (key_name, response['KeyMaterial'])

def get_instances_by_user():
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:UserId',
                'Values': [str(current_user.id)]
            },
            {
                'Name': 'tag:UserEmail',
                'Values': [str(current_user.email)]
            }
        ]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance)

    return instances

def get_instances_info():
    def extract_info_from_instance(instance):
        instance_id = instance['InstanceId']
        public_ip = instance.get('PublicIpAddress', None)
        public_dns = instance.get('PublicDnsName', None)
        state = instance['State']['Name']
        return instance_id, public_ip, public_dns, state

    instances = get_instances_by_user()
    instances_info = [extract_info_from_instance(instance) for instance in instances] 
    return instances_info

def process_ec2_configuration(image_id, instance_type, key_name, user_id, email, security_group_id):
    response = ec2_client.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        KeyName=key_name,
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'UserId',
                        'Value': f'{user_id}'
                    },
                    {
                        'Key': 'UserEmail',
                        'Value': f'{email}'
                    }
                ]
            }
        ]
    )
    return response

def launch_aws_instance(image_id, instance_type):
    try:
        key_name, private_key = process_key_pair()

        # Create or get the existing security group for the user
        security_group_id = get_security_group_id_for_user(current_user.id, current_user.email)

        if not security_group_id:
            security_group_id = create_security_group(current_user.id, current_user.email)

        response = process_ec2_configuration(image_id=image_id,
                                             instance_type=instance_type, 
                                             key_name=key_name, 
                                             user_id=current_user.id, 
                                             email=current_user.email,
                                             security_group_id=security_group_id)
        instance_id = response['Instances'][0]['InstanceId']

        if instance_id and private_key:
            flash('Instance created!', category='success')
            print('Instance created!')

            # Wait for the instance to be in a running state and to have a public IP address
            for i in range(10): 
                instance_info = ec2_client.describe_instances(InstanceIds=[instance_id])
                instance = instance_info['Reservations'][0]['Instances'][0]
                public_ip = instance.get('PublicIpAddress')
                public_dns = instance.get('PublicDnsName')

                if public_ip and public_dns:
                    return instance_id, private_key, public_ip, public_dns
                sleep(0.5) 

            # If the instance did not get a public IP within the waiting period
            flash('Instance created but public IP was not assigned within the expected time.', category='warning')
            return instance_id, private_key, None, None
        else:
            flash('Error creating an instance', category='error')
            return None
        
    except Exception as e:
        flash('Termination of instance has failed. Error occured.')
        print('An error occurred at launch of an instance: ', e)

def terminate_aws_instance(server_id):
    if server_id:
        try:
            # Retrieve key pair first before instance termination
            ec2_resource = resource('ec2')
            instance = ec2_resource.Instance(server_id)
            key_name = instance.key_name

            # Attempt to delete the associated key pair first
            if key_name:
                try:
                    ec2_client.delete_key_pair(KeyName=key_name)
                    print('Deleted key pair successfuly.')
                except ClientError as e:
                    print('Failed to delete key pair.')

            # Terminating instance
            response = ec2_client.terminate_instances(InstanceIds=[server_id])
            print('Deleted instance successfuly.')
            flash('Termination of instance has been successful.')

        except Exception as e:
            flash('Termination of instance has failed. Error occured.')
            print('An error occurred at termination of an instance: ', e)

def create_security_group(user_id, user_email):
    sg_name = f"sg_{user_id}_{user_email}"
    try:
        response = ec2_client.create_security_group(
            GroupName=sg_name,
            Description=f"Security group created!"
        )
        security_group_id = response['GroupId']

        # Add rules to the security group (adjust ports and protocols as needed)
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,  # SSH
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,  # HTTP
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,  # HTTPS
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )

        return security_group_id
    except ClientError as e:
        print(f"Error creating security group!")
        return None
    
def get_security_group_id_for_user(user_id, user_email):
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
    
def choose_root(image_id):
    if image_id == 'ami-0c93065e42589c42b':
        return 'alpine'