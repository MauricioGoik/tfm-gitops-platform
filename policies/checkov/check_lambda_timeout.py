from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class LambdaTimeoutCheck(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Lambda function has explicit timeout under 300s"
        id = "CKV_CUSTOM_LAMBDA_001"
        supported_resources = ["aws_lambda_function"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id,
                        categories=categories,
                        supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        timeout = conf.get("timeout", [None])
        if isinstance(timeout, list):
            timeout = timeout[0]
        # Timeout debe estar definido y ser menor a 300s
        if timeout and int(timeout) < 300:
            return CheckResult.PASSED
        return CheckResult.FAILED

scanner = LambdaTimeoutCheck()
