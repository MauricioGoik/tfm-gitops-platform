package terraform

import rego.v1

# ============================================================
# REGLA 1: Solo permitir recursos en eu-west-1
# ============================================================
deny contains msg if {
  resource := input.resource_changes[_]
  resource.change.actions[_] != "delete"
  resource.type == "aws_s3_bucket"
  region := resource.change.after.region
  region != null
  region != "eu-west-1"
  msg := sprintf(
    "DENY: Recurso '%v' se crearía en región '%v'. Solo se permite eu-west-1.",
    [resource.address, region]
  )
}

# ============================================================
# REGLA 2: S3 debe tener encryption activada
# ============================================================
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket"
  resource.change.actions[_] != "delete"
  not has_encryption(resource.address)
  msg := sprintf(
    "DENY: S3 bucket '%v' no tiene encryption configurada.",
    [resource.address]
  )
}

has_encryption(_) if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket_server_side_encryption_configuration"
  resource.change.after.bucket != null
}

# ============================================================
# REGLA 3: IAM policies no pueden tener Action: "*"
# ============================================================
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_iam_user_policy"
  resource.change.actions[_] != "delete"
  policy := json.unmarshal(resource.change.after.policy)
  statement := policy.Statement[_]
  statement.Effect == "Allow"
  statement.Action == "*"
  msg := sprintf(
    "DENY: IAM policy '%v' tiene Action: '*'. Usa permisos específicos.",
    [resource.address]
  )
}

# ============================================================
# REGLA 4: Lambda debe tener timeout explícito
# ============================================================
warn contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_lambda_function"
  resource.change.actions[_] != "delete"
  not resource.change.after.timeout
  msg := sprintf(
    "WARN: Lambda '%v' no tiene timeout explícito. El default es 3s.",
    [resource.address]
  )
}

# ============================================================
# REGLA 5: S3 no puede ser completamente público
# Excepción: buckets de dashboard/static hosting con
# bucket policy explícita están permitidos
# ============================================================
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket_public_access_block"
  resource.change.actions[_] != "delete"
  resource.change.after.block_public_acls == false
  resource.change.after.block_public_policy == false
  resource.change.after.restrict_public_buckets == false
  not contains(resource.address, "dashboard")
  msg := sprintf(
    "DENY: S3 bucket '%v' tiene acceso público completamente abierto sin ser un bucket de hosting.",
    [resource.address]
  )
}
