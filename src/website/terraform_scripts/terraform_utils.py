import subprocess
import paramiko
import io
from website.models import db, Instance
from pathlib import Path
from flask_login import current_user
from flask import flash
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

current_folder = Path(__file__).parent.absolute()

# Terraform scripts paths
aws_instance_script = current_folder / 'aws_instance.tf' 

def generate_key_pair():
    key = paramiko.RSAKey.generate(4096)

    private_key_buffer = io.StringIO()
    key.write_private_key(private_key_buffer)
    private_key = private_key_buffer.getvalue()

    public_key = key.get_base64()
    public_key = "ssh-rsa " + public_key + " example@gmail.com"

    return private_key, public_key

def launch_aws_instance(instance_type):
    try:
        private_key, public_key = generate_key_pair()

        subprocess.run(["terraform", "init"], cwd=current_folder)
        # subprocess.run(["terraform", "plan", "-var", f"instance_type={instance_type}", "-var", f"public_key={public_key}"], check=True, cwd=current_folder)
        subprocess.run(["terraform", "apply", "-var", f"instance_type={instance_type}", "-var", f"public_key={public_key}"], check=True, cwd=current_folder)

        new_instance = Instance(user_id=current_user.id)
        db.session.add(new_instance)
        db.session.commit()

        flash('Instance created!', category='success')
    except Exception as e:
        print("Error executing Terraform:", e)
