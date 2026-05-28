# ADR-004: Imágenes Docker Multi-Arquitectura

**Estado:** Aceptado
**Fecha:** 2026-05

## Contexto

El desarrollo se hace en Mac M4 (ARM64) pero los entornos de producción
típicamente usan AMD64. Necesitamos que las imágenes funcionen en ambas.

## Decisión

Usar Docker Buildx con `--platform linux/amd64,linux/arm64` en el pipeline CI.

## Razones

- Desarrollo nativo en M4 sin emulación (mejor rendimiento local)
- Compatible con AWS Graviton (ARM64) que es más barato en producción
- Una sola imagen sirve para todos los entornos
- GitHub Actions soporta Buildx nativamente

## Alternativas consideradas

- **Solo AMD64** — funciona pero desperdicia la ventaja de M4
- **Solo ARM64** — no compatible con la mayoría de servidores cloud
- **Emulación QEMU** — funciona pero builds muy lentos

## Consecuencias

- Build más lento (~2x) por compilar dos arquitecturas
- Mayor compatibilidad con cualquier entorno de despliegue
- Preparado para AWS Graviton sin cambios adicionales
