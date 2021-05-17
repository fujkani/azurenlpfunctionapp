
# Eventually will put here common functions shared by all functions..


from sentry_sdk import init, capture_message
from sentry_sdk.integrations.serverless import serverless_function


init(
    os.environ["SENTRY_DSN"],
    environment=os.environ["AZURE_FUNCTIONS_ENVIRONMENT"].lower(),

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
)

