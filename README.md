# 🚀 AI-Powered GitOps Platform

> TFM — Máster Multicloud & DevOps

Pipeline GitOps de nivel producción con Policy-as-Code, Security Scanning automatizado y un **Agente de IA autónomo** que detecta vulnerabilidades y abre Pull Requests de remediación sin intervención humana.

![CI](https://github.com/MauricioGoik/tfm-gitops-platform/actions/workflows/ci.yaml/badge.svg)
![Security](https://github.com/MauricioGoik/tfm-gitops-platform/actions/workflows/security.yaml/badge.svg)

---

## 🎯 ¿Qué hace este proyecto?

1. **Developer hace push** → GitHub Actions construye la imagen Docker (ARM64 + AMD64)
2. **Security gates** → Trivy, Checkov y OPA/Conftest escanean imagen, IaC y manifiestos
3. **ArgoCD despliega** → sincroniza automáticamente el clúster Kubernetes desde Git
4. **Gatekeeper enforza** → admission control rechaza pods que violan políticas de seguridad
5. **AI Agent actúa** → Lambda invoca Groq (Llama 3.3 70B), analiza CVEs y abre PRs automáticamente

**Todo esto ocurre en menos de 3 minutos desde el push hasta el despliegue.**

---

## 🏗️ Arquitectura

    graph TB
        Dev[Developer] -->|git push| GH[GitHub]
        GH -->|trigger| CI[GitHub Actions CI]
        CI -->|build multi-arch| GHCR[GHCR Registry]
        CI -->|scan| Trivy[Trivy CVE Scanner]
        CI -->|scan| Checkov[Checkov IaC Scanner]
        CI -->|validate| Conftest[OPA Conftest]
        CI -->|generate| SBOM[SBOM Syft]
        Trivy -->|SARIF| Security[GitHub Security Tab]
        Checkov -->|SARIF| Security
        SBOM -->|upload| S3[AWS S3]
        Trivy -->|CVEs found| Lambda[AWS Lambda]
        Lambda -->|analyze| Groq[Groq API Llama 3.3 70B]
        Groq -->|fix recommendation| Lambda
        Lambda -->|open PR| GH
        GHCR -->|watch| ArgoCD[ArgoCD]
        ArgoCD -->|deploy| K8s[kind Cluster]
        K8s -->|enforce| Gatekeeper[OPA Gatekeeper]
        Gatekeeper -->|deny violations| K8s

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| **GitOps** | ArgoCD + Kustomize | Sincronización Git a Cluster |
| **CI/CD** | GitHub Actions | Pipeline automatizado |
| **Registry** | GitHub Container Registry | Imágenes ARM64 + AMD64 |
| **IaC** | Terraform + Terraform Cloud | Infraestructura AWS como código |
| **Security Scanning** | Trivy + Checkov + Syft | CVEs, misconfigs, SBOM |
| **Policy-as-Code** | OPA + Gatekeeper + Conftest | Políticas versionadas en Git |
| **AI Agent** | AWS Lambda + Groq | Remediación autónoma de vulnerabilidades |
| **LLM** | Llama 3.3 70B (Groq) | Análisis y fix de CVEs |
| **Cloud** | AWS Free Tier | S3, Lambda, IAM |
| **Cluster** | kind (Kubernetes in Docker) | Entorno local de producción |

---

## 🔒 Security Pipeline

Cada Pull Request pasa por estos gates automáticamente:

    PR abierto
    ├── Trivy Container Scan     → CVEs en imagen Docker
    ├── Trivy IaC Scan           → Misconfigs en Terraform
    ├── Checkov Deep Scan        → 1000+ checks de seguridad IaC
    ├── Syft SBOM Generation     → Software Bill of Materials
    ├── OPA/Conftest Policies    → Políticas personalizadas en Rego
    └── Terraform Plan + OPA     → Validación de infra antes del apply

    Si pasa todo → merge permitido
    Si falla CRITICAL → merge bloqueado

---

## 🤖 AI Security Agent

El agente autónomo es el componente diferenciador del proyecto:

    Trivy detecta CVE-XXXX-YYYY (HIGH/CRITICAL)
        └── GitHub Actions invoca AWS Lambda
            └── Lambda llama a Groq API (Llama 3.3 70B)
                └── IA analiza: riesgo, fix, urgencia
                    └── Se abre PR automáticamente con:
                        ├── Tabla de detalles del CVE
                        ├── Análisis de riesgo en lenguaje natural
                        ├── Fix recomendado paso a paso
                        └── Labels: security, automated, ai-generated

**Tiempo desde detección hasta PR: menos de 30 segundos**

---

## 📋 Policy-as-Code

Las políticas de seguridad son código versionado en Git:

    policies/
    ├── kubernetes/
    │   ├── main.rego        # No latest, no root, resource limits
    │   └── services.rego    # No LoadBalancer
    └── terraform/
        └── main.rego        # Solo eu-west-1, S3 encryption, no IAM wildcard

OPA Gatekeeper enforza las políticas directamente en el admission controller de Kubernetes — ningún pod puede entrar al clúster si viola las reglas, independientemente de quién lo despliegue.

---

## 🚀 Setup en 5 minutos

### Prerequisitos

- Docker Desktop
- kubectl, kind, helm, terraform
- AWS CLI configurado
- Cuenta Groq (gratuita)

### Levantar el entorno

    # 1. Clonar el repo
    git clone https://github.com/MauricioGoik/tfm-gitops-platform.git
    cd tfm-gitops-platform

    # 2. Levantar cluster Kubernetes
    kind create cluster --config kind-config.yaml

    # 3. Instalar ArgoCD
    helm repo add argo https://argoproj.github.io/argo-helm
    helm install argocd argo/argo-cd --namespace argocd --create-namespace

    # 4. Desplegar la aplicacion
    kubectl apply -f argocd-app.yaml

    # 5. Acceder a ArgoCD
    kubectl port-forward svc/argocd-server -n argocd 8080:80

    # 6. Infraestructura AWS (opcional)
    cd infra/aws && terraform apply

---

## 📁 Estructura del Repositorio

    tfm-gitops-platform/
    ├── apps/demo-web/          # Aplicacion demo (Flask + Docker ARM64)
    ├── k8s/
    │   ├── base/               # Manifiestos Kubernetes base
    │   ├── overlays/dev/       # Configuracion entorno dev
    │   └── gatekeeper/         # OPA Gatekeeper policies
    ├── infra/aws/              # Infraestructura AWS (Terraform)
    ├── policies/
    │   ├── kubernetes/         # Politicas OPA para K8s (Rego)
    │   ├── terraform/          # Politicas OPA para Terraform (Rego)
    │   └── checkov/            # Checks personalizados Checkov
    ├── agent/                  # Agente IA (Python + Groq)
    ├── scripts/                # Scripts de utilidad
    └── .github/workflows/      # Pipelines CI/CD
        ├── ci.yaml             # Build, push, SBOM
        └── security.yaml       # Trivy, Checkov, OPA, AI Agent

---

## 📊 Estado del Proyecto

- [x] Fase 1 — GitOps Foundation
- [x] Fase 2 — Security Scanning
- [x] Fase 3 — Policy-as-Code
- [x] Fase 4 — AI Agent
- [x] Fase 5 — Documentacion

---

## 🏆 Decisiones de Arquitectura

Ver docs/adr/ para las Architecture Decision Records completas.

- ADR-001: GitOps con ArgoCD
- ADR-002: Policy-as-Code con OPA/Gatekeeper
- ADR-003: AI Agent con Groq y Llama 3.3 70B
- ADR-004: Imagenes Docker Multi-Arquitectura

---

## 👨‍💻 Autor

**Mauricio Goik** — Máster Multicloud & DevOps

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/mauriciogoik/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/MauricioGoik)
