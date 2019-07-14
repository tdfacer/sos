variable "aws_region" {
  default = "us-east-1"
}
variable "aws_credentials_path" {
  default = "~/.aws/credentials"
}

variable "aws_profile" {
  default = "default"
}

terraform {
  backend "s3" {
    bucket         = "terrafacer"
    key            = "sos/infrastructure.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform"
    encrypt        = true
  }
}

provider "aws" {
  region                  = "${var.aws_region}"
  shared_credentials_file = "${var.aws_credentials_path}"
  profile                 = "${var.aws_profile}"
}

module "sos-infrasctructure" {
  source = "git::https://github.com/tdfacer/terrafacer.git?ref=master//terraform/modules/sos"
}
