
from pathlib import Path
from flask_login import current_user
from flask import flash
from boto3 import Session, resource
from botocore.exceptions import ClientError
from datetime import datetime
from uuid import uuid4

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
        state = instance['State']['Name']
        return instance_id, public_ip, state

    instances = get_instances_by_user()
    instances_info = [extract_info_from_instance(instance) for instance in instances] 
    return instances_info

def process_ec2_configuration(instance_type, key_name, user_id):
    response = ec2_client.run_instances(
        ImageId='ami-0c93065e42589c42b',
        InstanceType=instance_type,
        KeyName=key_name,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'UserId',
                        'Value': f'{user_id}'
                    }
                ]
            }
        ]
    )
    return response

def launch_aws_instance(instance_type):
    try:
        key_name, private_key = process_key_pair()
        response = process_ec2_configuration(instance_type=instance_type, key_name=key_name, user_id=current_user.id)
        instance_id = response['Instances'][0]['InstanceId']

        if instance_id:
            flash('Instance created!', category='success')
            print('Deleted key pair successfuly.')
            return private_key
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
            flash('Termination of instance has been successful.')

        except Exception as e:
            flash('Termination of instance has failed. Error occured.')
            print('An error occurred at termination of an instance: ', e)