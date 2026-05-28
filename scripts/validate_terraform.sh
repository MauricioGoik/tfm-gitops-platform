#!/bin/bash
set -e

echo "=== Terraform Policy Validation ==="

cd "$(dirname "$0")/../infra/aws"

echo "1. Generando plan de Terraform..."
terraform plan -out=tfplan.binary

echo "2. Convirtiendo plan a JSON..."
terraform show -json tfplan.binary > tfplan.json

echo "3. Validando con OPA/Conftest..."
conftest test tfplan.json \
  --policy ../../policies/terraform/ \
  --namespace terraform \
  --all-namespaces

echo "=== Validación completada ==="

# Limpieza
rm -f tfplan.binary tfplan.json
