variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "project_prefix" {
  description = "Prefix used for all resources"
  type        = string
  default     = "multibrand-retail"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "db_name" {
  description = "Name of the Postgres database"
  type        = string
  default     = "retail_serving"
}

variable "db_username" {
  description = "Master username for PostgreSQL"
  type        = string
  default     = "retail_admin"
}

variable "db_password" {
  description = "Master password for PostgreSQL. In a real environment, avoid hardcoding this."
  type        = string
  sensitive   = true
  default     = "SuperSecurePassword123!"
}
