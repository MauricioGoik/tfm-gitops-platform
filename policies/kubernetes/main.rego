package main

import rego.v1

# REGLA 1: Prohibir imagen con tag :latest
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  endswith(container.image, ":latest")
  msg := sprintf(
    "DENY: Container '%v' usa imagen con tag :latest. Usa un tag específico.",
    [container.name]
  )
}

# REGLA 2: Prohibir correr como root
deny contains msg if {
  input.kind == "Deployment"
  not input.spec.template.spec.securityContext.runAsNonRoot
  msg := "DENY: Deployment no tiene runAsNonRoot: true en el securityContext."
}

# REGLA 3: Prohibir deployments sin resource limits
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.resources.limits
  msg := sprintf(
    "DENY: Container '%v' no tiene resource limits definidos.",
    [container.name]
  )
}

# REGLA 4: Prohibir deployments sin resource requests
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.resources.requests
  msg := sprintf(
    "DENY: Container '%v' no tiene resource requests definidos.",
    [container.name]
  )
}

# REGLA 5: Warning si no hay readiness probe
warn contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.readinessProbe
  msg := sprintf(
    "WARN: Container '%v' no tiene readinessProbe definido.",
    [container.name]
  )
}

# REGLA 6: Warning si no hay liveness probe
warn contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.livenessProbe
  msg := sprintf(
    "WARN: Container '%v' no tiene livenessProbe definido.",
    [container.name]
  )
}

# REGLA 7: Prohibir namespace default
deny contains msg if {
  input.kind == "Deployment"
  input.metadata.namespace == "default"
  msg := "DENY: No desplegar en el namespace 'default'. Usa un namespace dedicado."
}
