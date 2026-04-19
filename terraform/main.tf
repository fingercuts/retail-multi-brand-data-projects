terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------
# Storage Layer: Raw Data Lake (S3)
# ---------------------------------------------------------
resource "aws_s3_bucket" "data_lake" {
  bucket        = "${var.project_prefix}-data-lake-${var.environment}"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "data_lake_versioning" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# ---------------------------------------------------------
# Serving Layer: PostgreSQL Database (RDS)
# ---------------------------------------------------------
resource "aws_db_instance" "serving_db" {
  identifier        = "${var.project_prefix}-serving-db-${var.environment}"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password # In production, source this from AWS Secrets Manager

  skip_final_snapshot = true
  publicly_accessible = false
}

# ---------------------------------------------------------
# API Layer: ECS Cluster for FastAPI Serving
# ---------------------------------------------------------
resource "aws_ecs_cluster" "api_cluster" {
  name = "${var.project_prefix}-api-cluster-${var.environment}"
}

# Example wrapper for ECR (Elastic Container Registry) to store the FastAPI Docker Image
resource "aws_ecr_repository" "api_repo" {
  name                 = "${var.project_prefix}-api-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
