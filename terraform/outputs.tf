output "s3_data_lake_bucket_name" {
  description = "Name of the S3 bucket acting as the raw data lake"
  value       = aws_s3_bucket.data_lake.bucket
}

output "rds_endpoint" {
  description = "Endpoint for the PostgreSQL Serving Layer Database"
  value       = aws_db_instance.serving_db.endpoint
}

output "ecr_repository_url" {
  description = "ECR Repository URL for pushing the FastAPI Docker image"
  value       = aws_ecr_repository.api_repo.repository_url
}
