output "alb_dns_url" {
  description = "The public ALB DNS name"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecr_repository_url" {
  description = "The ECR repo URL for docker push"
  value       = aws_ecr_repository.app.repository_url
}

output "rds_endpoint" {
  description = "The RDS connection endpoint"
  value       = aws_db_instance.main.endpoint
}

output "redis_endpoint" {
  description = "The ElastiCache endpoint"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "ecs_cluster_name" {
  description = "The ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "The ECS service name"
  value       = aws_ecs_service.app.name
}

output "vpc_id" {
  description = "The VPC ID"
  value       = aws_vpc.main.id
}
