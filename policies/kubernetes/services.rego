package main

import rego.v1

# REGLA: Prohibir Services de tipo LoadBalancer
deny contains msg if {
  input.kind == "Service"
  input.spec.type == "LoadBalancer"
  msg := sprintf(
    "DENY: Service '%v' usa type LoadBalancer. Usa ClusterIP con Ingress.",
    [input.metadata.name]
  )
}
