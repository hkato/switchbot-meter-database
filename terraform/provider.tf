terraform {
  required_version = "~>1.13.1"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.12.0"
    }

    sops = {
      source  = "carlpett/sops"
      version = "~> 1.2.1"
    }
  }

  backend "s3" {
  }
}
