import os

GCD_API_KEY = os.environ.get("GCP_API_KEY")
assert GCD_API_KEY is not None, "GCD_API_KEY required"

GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
assert GOOGLE_APPLICATION_CREDENTIALS is not None, "GOOGLE_APPLICATION_CREDENTIALS required"

