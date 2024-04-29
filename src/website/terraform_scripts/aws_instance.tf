provider "aws" {
  region = "eu-west-1"
}

resource "aws_key_pair" "public_key_config" {
  key_name   = "example_key_name"
  public_key = var.public_key
}

data "aws_security_group" "ssh_security_group" {
  name ="SSHAccessForUsers"
}

resource "aws_instance" "aws_instance_config" {
  # AMI version: alpine-3.19.0-x86_64-bios-tiny-r0
  ami           = "ami-0c93065e42589c42b"
  instance_type = var.instance_type
  key_name = aws_key_pair.public_key_config.key_name
  security_groups = [data.aws_security_group.ssh_security_group.name]
}