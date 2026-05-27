from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.kubernetes.checks.resource.base_resource_check import BaseK8Check

class K8sReadinessProbeCheck(BaseK8Check):
    def __init__(self):
        name = "Ensure Kubernetes Deployment has readinessProbe defined"
        id = "CKV_CUSTOM_K8S_001"
        supported_entities = ["Deployment"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id,
                        categories=categories,
                        supported_entities=supported_entities)

    def scan_resource_conf(self, conf):
        containers = conf.get("spec", {}).get("template", {}).get(
            "spec", {}).get("containers", [])
        for container in containers:
            if not container.get("readinessProbe"):
                return CheckResult.FAILED
        return CheckResult.PASSED

scanner = K8sReadinessProbeCheck()
