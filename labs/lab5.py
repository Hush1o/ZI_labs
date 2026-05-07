import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import dsa, utils
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

def generate_keys(key_size: int = 2048):
    private_key = dsa.generate_private_key(key_size=key_size)
    public_key = private_key.public_key()
    return private_key, public_key

def save_private_key(private_key, path: str, password: bytes | None = None):
    enc_algo = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc_algo,
    )
    with open(path, "wb") as f:
        f.write(pem)


def save_public_key(public_key, path: str):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open(path, "wb") as f:
        f.write(pem)


def load_private_key(path: str, password: bytes | None = None):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(), password=password, backend=default_backend()
        )


def load_public_key(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read(), backend=default_backend())



def sign_message(private_key, message: str) -> bytes:
    data = message.encode()
    signature = private_key.sign(data, hashes.SHA256())
    return signature


def verify_message(public_key, message: str, signature: bytes) -> bool:
    try:
        public_key.verify(signature, message.encode(), hashes.SHA256())
        return True
    except InvalidSignature:
        return False


def sign_file(private_key, file_path: str, sig_path: str):

    chosen_hash = hashes.SHA256()
    hasher = hashes.Hash(chosen_hash, backend=default_backend())

    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)

    digest = hasher.finalize()
    signature = private_key.sign(digest, utils.Prehashed(chosen_hash))

    with open(sig_path, "w") as f:
        f.write(signature.hex())

    print(f"[+] Підпис збережено: {sig_path}")
    print(f"    Hex: {signature.hex()[:64]}...")
    return signature


def verify_file(public_key, file_path: str, sig_path: str) -> bool:

    with open(sig_path, "r") as f:
        signature = bytes.fromhex(f.read().strip())

    chosen_hash = hashes.SHA256()
    hasher = hashes.Hash(chosen_hash, backend=default_backend())

    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)

    digest = hasher.finalize()

    try:
        public_key.verify(signature, digest, utils.Prehashed(chosen_hash))
        return True
    except InvalidSignature:
        return False


def save_result(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] Результат збережено: {path}")


