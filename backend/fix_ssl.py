import os
import certifi
import ssl
import sys

print(f"Python: {sys.version}")
print(f"Certifi path: {certifi.where()}")

# Try 1: Explicitly point to certifi
print("\n--- Attempt 1: Using certifi bundle ---")
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()
# Remove disable flags if present
if 'HF_HUB_DISABLE_SSL_VERIFY' in os.environ:
    del os.environ['HF_HUB_DISABLE_SSL_VERIFY']

try:
    from huggingface_hub import snapshot_download
    print("Downloading model...")
    path = snapshot_download("nomic-ai/nomic-embed-text-v1.5", force_download=False)
    print(f"SUCCESS! Downloaded to: {path}")
    sys.exit(0)
except Exception as e:
    print(f"FAILED: {e}")

# Try 2: Nuclear Option - Disable Everything
print("\n--- Attempt 2: Disabling SSL Verification completely ---")
os.environ['HF_HUB_DISABLE_SSL_VERIFY'] = '1'
if 'REQUESTS_CA_BUNDLE' in os.environ:
    del os.environ['REQUESTS_CA_BUNDLE']
if 'SSL_CERT_FILE' in os.environ:
    del os.environ['SSL_CERT_FILE']

# Patch SSL context behavior
try:
    _create_unverified_https_context = ssl._create_unverified_context
    ssl._create_default_https_context = _create_unverified_https_context
    print("Patched ssl._create_default_https_context")
except AttributeError:
    pass

try:
    print("Downloading model (unverified)...")
    path = snapshot_download("nomic-ai/nomic-embed-text-v1.5", force_download=False)
    print(f"SUCCESS! Downloaded to: {path}")
except Exception as e:
    print(f"FAILED AGAIN: {e}")
