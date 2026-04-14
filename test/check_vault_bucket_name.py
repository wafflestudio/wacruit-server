from __future__ import annotations

import base64
import json
import os
import sys
from typing import cast

from dotenv import load_dotenv
import oci
from oci.secrets.models import SecretBundle

from wacruit.src.settings import settings


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required env: {name}")
    return value


def _make_secrets_client() -> oci.secrets.SecretsClient:
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        return oci.secrets.SecretsClient({}, signer=signer)
    except Exception:  # pylint: disable=broad-exception-caught
        profile = os.getenv("OCI_CLI_PROFILE", "DEFAULT")
        config = oci.config.from_file(profile_name=profile)
        return oci.secrets.SecretsClient(config)


def main() -> int:
    try:
        load_dotenv(".env.test")
        secret_id = os.getenv("OCI_SECRET_OCID") or settings.oci_secret_ocid
        if not secret_id:
            raise ValueError(
                "Missing OCI secret id. Set OCI_SECRET_OCID in .env.test "
                "or run with ENV=dev/prod so settings.oci_secret_ocid is available."
            )
        key_name = os.getenv("OCI_BUCKET_KEY_NAME", "portfolio_bucket_name")

        client = _make_secrets_client()
        bundle_response = client.get_secret_bundle(secret_id=secret_id)
        if bundle_response is None or bundle_response.data is None:
            raise ValueError(f"Secret bundle is empty for {secret_id}")
        bundle = cast(SecretBundle, bundle_response.data)
        if bundle.secret_bundle_content is None:
            raise ValueError(f"Secret bundle content is empty for {secret_id}")
        base64_secret_content = bundle.secret_bundle_content.content
        decoded = base64.b64decode(base64_secret_content).decode("utf-8")
        secret_data = json.loads(decoded)

        if key_name not in secret_data:
            print(f"[ERROR] Key not found in vault secret: {key_name}")
            print(f"Available keys: {sorted(secret_data.keys())}")
            return 1

        print(f"Vault key found: {key_name}")
        print(f"Bucket name: {secret_data[key_name]}")
        return 0
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
