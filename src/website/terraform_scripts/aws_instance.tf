provider "aws" {
  region = "your-aws-region"
}

resource "aws_instance" "example" {
  ami           = "your-ami-id"
  instance_type = "t2.micro"  # Or use a variable here
}