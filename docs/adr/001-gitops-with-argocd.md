# ADR-001: GitOps con ArgoCD

**Estado:** Aceptado
**Fecha:** 2026-05

## Contexto

Necesitamos un mecanismo para desplegar aplicaciones en Kubernetes de forma
reproducible, auditable y sin acceso manual al clúster.

## Decisión

Usar ArgoCD como operador GitOps con el patrón App of Apps.

## Razones

- Git como única fuente de verdad — cualquier cambio pasa por PR y revisión
- `selfHeal: true` revierte cambios manuales automáticamente
- App of Apps permite gestionar múltiples aplicaciones desde un solo repo
- ArgoCD es el estándar de facto en la industria (CNCF graduated project)

## Alternativas consideradas

- **Flux** — igualmente válido pero menor adopción en el mercado español
- **Jenkins X** — demasiada complejidad para este proyecto
- **Deploy manual con kubectl** — no auditable, no reproducible

## Consecuencias

- Todo cambio en el clúster debe pasar por Git
- El clúster siempre converge al estado del repositorio
- Mayor trazabilidad y auditabilidad de despliegues
