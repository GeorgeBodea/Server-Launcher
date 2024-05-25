
from website.models import db, Instance
from pathlib import Path
from flask_login import current_user
from flask import flash
from boto3 import Session, client, resource
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

def process_ec2_configuration(instance_type, key_name):
    response = ec2_client.run_instances(
        ImageId='ami-0c93065e42589c42b',
        InstanceType=instance_type,
        KeyName=key_name,
        MinCount=1,
        MaxCount=1
    )
    return response


def launch_aws_instance(instance_type):
    try:
        key_name, private_key = process_key_pair()
        response = process_ec2_configuration(instance_type=instance_type, key_name=key_name)
        instance_id = response['Instances'][0]['InstanceId']

        if instance_id:
            new_instance = Instance(aws_instance_id=instance_id, user_id=current_user.id)
            db.session.add(new_instance)
            db.session.commit()
            flash('Instance created!', category='success')

            return private_key
        else:
            flash('Error creating instance', category='error')
            return None
        
    except Exception as e:
        print("Error executing Terraform:", e)

def terminate_aws_instance(server_id):
    instance_to_delete = Instance.query.get(server_id)
    if instance_to_delete:
        try:
            ec2_client = client('ec2')
            response = ec2_client.terminate_instances(InstanceIds=[instance_to_delete.aws_instance_id])

            ec2_resource = resource('ec2')
            instance = ec2_resource.Instance(instance_to_delete.aws_instance_id)
            key_name = instance.key_name
            ec2_client.delete_key_pair(KeyName=key_name)

            db.session.delete(instance_to_delete)
            db.session.commit()
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                db.session.delete(instance_to_delete)
                db.session.commit()
            else: 
                print("An error occurred:", e)