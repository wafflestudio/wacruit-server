import base64
import json

import oci

from wacruit.src.settings import settings
from wacruit.src.utils.singleton import SingletonMeta


class OCISecretManager(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.secret_id = settings.oci_secret_ocid
        self.client = None
        if settings.env in ["local", "test"]:
            return
        try:
            self.signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            self.client = oci.secrets.SecretsClient({}, signer=self.signer)
        except Exception:  # pylint: disable=broad-exception-caught
            self.config = oci.config.from_file()
            self.client = oci.secrets.SecretsClient(self.config)
        self.secret_id = settings.oci_secret_ocid

    def is_available(self) -> bool:
        if settings.env in ["local", "test"]:
            return False
        try:
            assert self.client is not None
            self.client.get_secret_bundle(secret_id=self.secret_id)
            return True
        except Exception as e:
            raise ValueError(f"OCI Vault is not available for {self.secret_id}") from e

    def get_secret(self, key: str) -> str:
        assert self.is_available(), "OCI Vault is not available"
        assert self.client is not None
        bundle = self.client.get_secret_bundle(secret_id=self.secret_id)
        assert bundle is not None
        bundle = bundle.data

        base64_secret_content = bundle.secret_bundle_content.content
        decoded_secret_content = base64.b64decode(base64_secret_content).decode("utf-8")

        secret_data = json.loads(decoded_secret_content)
        return secret_data[key]
