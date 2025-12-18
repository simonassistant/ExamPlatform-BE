import os

from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_sts20150401.client import Client as Sts20150401Client
from alibabacloud_sts20150401 import models as sts_20150401_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

def get_ali_credentials(session_name: str='session_ep', duration: int=900):
    credential = CredentialClient()
    config = open_api_models.Config(
        credential=credential
    )
    config.endpoint = os.getenv('ALI_ENDPOINT')
    config.access_key_id = os.getenv('ALI_ACCESS_KEY_ID')
    config.access_key_secret = os.getenv('ALI_ACCESS_KEY_SECRET')
    client = Sts20150401Client(config)

    assume_role_request = sts_20150401_models.AssumeRoleRequest(
        duration_seconds=duration,
        role_session_name=session_name,
        role_arn=os.getenv('ALI_ROLE_ARN')
    )
    runtime = util_models.RuntimeOptions()
    try:
        response = client.assume_role_with_options(assume_role_request, runtime)
        return response.body.credentials
    except Exception as error:
        print(error)
    return None
