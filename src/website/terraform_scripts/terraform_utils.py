import subprocess
from pathlib import Path

current_folder = Path(__file__).parent.absolute()

# Terraform scripts paths
aws_instance_script = current_folder / 'aws_instance.tf' 

def launch_aws_instance(instance_type):
    try:
        subprocess.run(["terraform", "init"], cwd=current_folder)
        subprocess.run(["terraform", "apply", "-auto-approve", "-var", f"instance_type={instance_type}", str(aws_instance_script)], check=True, cwd=current_folder)
    except Exception as e:
        print("Error executing Terraform:", e)
