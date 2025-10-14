from isa_pipeline_hash import ISAPipelineHashProcessor
from vault import Vault

class VerificadorBoveda:
    def __init__(self, pipeline_processor: ISAPipelineHashProcessor = None):
        if pipeline_processor is None:
            self.processor = ISAPipelineHashProcessor()
        else:
            self.processor = pipeline_processor
        # Ensure a vault exists on the processor pipeline
        if not hasattr(self.processor.pipeline, 'vault') or self.processor.pipeline.vault is None:
            self.processor.pipeline.vault = Vault()

    def get_signature_components(self, signed_file):
        with open(signed_file, 'rb') as f:
            data = f.read()
        if len(data) < 32:
            raise ValueError("Signed file too small")
        signature_data = data[-32:]
        signature = tuple(int.from_bytes(signature_data[i*8:(i+1)*8], 'little') for i in range(4))
        return signature

    def verify_signed_file_with_vault(self, signed_file, vault_index=0):
        """Verify the signed file by asking the vault to produce the expected signature."""
        # Ensure the processor has the document and vault
        result = self.processor.verify_signed_file(signed_file, key={'use_vault': True, 'vault_index': vault_index})
        return result

    def recover_components_from_signature_with_key(self, signature, key):
        """Given a signature and a key, recover the original A,B,C,D by XOR'ing with key."""
        return tuple(s ^ key for s in signature)
