from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class S3VersioningCheck(BaseResourceCheck):
    def __init__(self):
        name = "Ensure S3 bucket has versioning enabled"
        id = "CKV_CUSTOM_S3_001"
        supported_resources = ["aws_s3_bucket_versioning"]
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, 
                        categories=categories, 
                        supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        versioning = conf.get("versioning_configuration", [{}])
        if isinstance(versioning, list):
            versioning = versioning[0]
        status = versioning.get("status", [""])[0]
        if status == "Enabled":
            return CheckResult.PASSED
        return CheckResult.FAILED

scanner = S3VersioningCheck()
