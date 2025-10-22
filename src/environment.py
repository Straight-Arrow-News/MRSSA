import json
import os

import boto3

OTEL_DEPLOYMENT_ENVIRONMENT = os.environ.get("OTEL_DEPLOYMENT_ENVIRONMENT")

session = boto3.session.Session()
secrets_client = session.client(
    service_name="secretsmanager", region_name=os.environ["AWS_REGION"]
)

grafana_secrets_name = "otel/grafana"
grafana_secrets = json.loads(
    secrets_client.get_secret_value(SecretId=grafana_secrets_name)["SecretString"]
)

OTEL_EXPORTER_OTLP_ENDPOINT = grafana_secrets["endpoint"]
GRAFANA_LABS_TOKEN = grafana_secrets["token"]

brightcove_secrets_name = "san/mrss/brightcove"
brightcove_secrets = json.loads(
    secrets_client.get_secret_value(SecretId=brightcove_secrets_name)["SecretString"]
)

BRIGHTCOVE_ACCOUNT_ID = brightcove_secrets["accountId"]
BRIGHTCOVE_POLICY_KEY = brightcove_secrets["searchPolicyId"]
