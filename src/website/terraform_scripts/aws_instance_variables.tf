variable "instance_type" {
  description = "The type of AWS instance to create"
  type        = string
}

variable "public_key" {
  description = "This is the public key that will be used to login into the instance"
  type        = string
}

variable "tag_refresh_value" {
  description = "This variable used to refresh the output of Terraform and update the id returned"
  type        = string
}