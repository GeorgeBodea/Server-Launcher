from flask_login import current_user
from time import sleep
from flask import flash
from boto3 import resource
from botocore.exceptions import ClientError

def get_instances_by_user(ec2_client):
    response = ec2_client.describe_instances(
        Filters=[
            {'Name': 'tag:UserId', 'Values': [str(current_user.id)]},
            {'Name': 'tag:UserEmail', 'Values': [str(current_user.email)]}
        ]
    )
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance)
    return instances

def get_instances_info(ec2_client):
    def extract_info_from_instance(instance):
        instance_id = instance['InstanceId']
        public_ip = instance.get('PublicIpAddress', None)
        public_dns = instance.get('PublicDnsName', None)
        state = instance['State']['Name']
        return instance_id, public_ip, public_dns, state

    instances = get_instances_by_user(ec2_client)
    instances_info = [extract_info_from_instance(instance) for instance in instances]
    return instances_info

def process_ec2_configuration(ec2_client, image_id, instance_type, key_name, user_id, email, security_group_id):
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
                    {'Key': 'UserId', 'Value': f'{user_id}'},
                    {'Key': 'UserEmail', 'Value': f'{email}'}
                ]
            }
        ]
    )
    return response

def launch_aws_instance(ec2_client, image_id, instance_type, process_key_pair, get_security_group_id_for_user, create_security_group):
    try:
        key_name, private_key = process_key_pair()
        security_group_id = get_security_group_id_for_user(current_user.id, current_user.email)

        if not security_group_id:
            security_group_id = create_security_group(current_user.id, current_user.email)

        response = process_ec2_configuration(ec2_client, image_id, instance_type, key_name, current_user.id, current_user.email, security_group_id)
        instance_id = response['Instances'][0]['InstanceId']

        if instance_id and private_key:
            flash('Instance created!', category='success')

            for _ in range(10):
                instance_info = ec2_client.describe_instances(InstanceIds=[instance_id])
                instance = instance_info['Reservations'][0]['Instances'][0]
                public_ip = instance.get('PublicIpAddress')
                public_dns = instance.get('PublicDnsName')

                if public_ip and public_dns:
                    return instance_id, private_key, public_ip, public_dns
                sleep(0.5)

            flash('Instance created but public IP was not assigned within the expected time.', category='warning')
            return instance_id, private_key, None, None
        else:
            flash('Error creating an instance', category='error')
            return None, None, None, None
    except Exception as e:
        flash('Termination of instance has failed. Error occurred.')
        print('An error occurred at launch of an instance: ', e)

def terminate_aws_instance(ec2_client, server_id):
    if server_id:
        try:
            ec2_resource = resource('ec2')
            instance = ec2_resource.Instance(server_id)
            key_name = instance.key_name

            if key_name:
                try:
                    ec2_client.delete_key_pair(KeyName=key_name)
                    print('Deleted key pair successfully.')
                except ClientError:
                    print('Failed to delete key pair.')

            ec2_client.terminate_instances(InstanceIds=[server_id])
            print('Deleted instance successfully.')
            flash('Termination of instance has been successful.')

        except Exception as e:
            flash('Termination of instance has failed. Error occurred.')
            print('An error occurred at termination of an instance: ', e)