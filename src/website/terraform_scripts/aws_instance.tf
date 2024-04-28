provider "aws" {
  region = "eu-west-1"
}

resource "aws_instance" "example" {
  # AMI version: alpine-3.19.0-x86_64-bios-tiny-r0
  ami           = "ami-0c93065e42589c42b"
  instance_type = var.instance_type
}