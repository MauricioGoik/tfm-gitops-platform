variable "aws_region" {
  description = "AWS region para todos los recursos"
  type        = string
  default     = "eu-west-1"
}

variable "environment" {
  description = "Entorno del proyecto"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "tfm-gitops-platform"
}

variable "groq_api_key" {
  description = "API key de Groq para el agente IA"
  type        = string
  sensitive   = true
}
