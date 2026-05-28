# ADR-002: Policy-as-Code con OPA/Gatekeeper

**Estado:** Aceptado
**Fecha:** 2026-05

## Contexto

Necesitamos enforcar políticas de seguridad de forma consistente tanto en CI
como en el clúster de Kubernetes, sin depender de revisiones manuales.

## Decisión

Usar OPA con dos capas:
1. Conftest en CI para validar antes del merge
2. Gatekeeper en el clúster como admission controller

## Razones

- Doble capa: CI bloquea antes del merge, Gatekeeper bloquea en el clúster
- Las políticas son código Rego versionado en Git
- Gatekeeper es un CNCF project, estándar en la industria
- Permite políticas personalizadas de negocio (no solo CVEs)

## Alternativas consideradas

- **Kyverno** — más sencillo pero menos flexible para políticas complejas
- **Pod Security Admission** — nativo de K8s pero muy limitado
- **Revisión manual** — no escala, propenso a errores humanos

## Consecuencias

- Ningún pod puede entrar al clúster sin cumplir las políticas
- Las políticas se revisan en PR como cualquier otro código
- Curva de aprendizaje de Rego para el equipo
