# ADR-003: Agente IA con Groq y Llama 3.3 70B

**Estado:** Aceptado
**Fecha:** 2026-05

## Contexto

Queremos automatizar la remediación de vulnerabilidades detectadas por Trivy,
reduciendo el tiempo entre detección y fix de horas a segundos.

## Decisión

Implementar un agente en AWS Lambda que usa Groq API (Llama 3.3 70B) para
analizar CVEs y abrir Pull Requests automáticos con fixes recomendados.

## Razones

- **Groq free tier** — suficiente para el proyecto sin coste
- **Llama 3.3 70B** — modelo open source de alta calidad para análisis técnico
- **Lambda** — serverless, sin coste en free tier (1M requests/mes)
- **PR automático** — el fix queda en Git, es revisable y auditable

## Alternativas consideradas

- **AWS Bedrock + Claude** — mejor calidad pero sin free tier
- **OpenAI GPT-4** — de pago, no alineado con objetivo de coste cero
- **Modelo local** — demasiados recursos computacionales

## Consecuencias

- Remediación autónoma en < 30 segundos desde detección
- El agente puede generar falsos positivos — revisión humana recomendada
- Dependencia de API externa (Groq) para el análisis
- Los PRs generados requieren revisión antes del merge
