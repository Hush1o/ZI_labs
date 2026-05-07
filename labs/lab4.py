import struct
import os
import time
import tempfile

from labs.lab3 import process_file
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


def generate_key_pair(key_size: int = 2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    return private_key, private_key.public_key()


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
        return serialization.load_pem_private_key(f.read(), password=password)


def load_public_key(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


_OAEP = padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None,
)

_RSA_MAX_CHUNK = 190


def encrypt_file(input_path: str, public_key, output_path: str | None = None) -> str:

    if output_path is None:
        output_path = input_path + ".enc"

    with open(input_path, "rb") as f:
        plaintext = f.read()

    chunks = [
        plaintext[i: i + _RSA_MAX_CHUNK]
        for i in range(0, len(plaintext), _RSA_MAX_CHUNK)
    ]

    with open(output_path, "wb") as f:
        f.write(struct.pack(">I", len(chunks)))
        f.write(struct.pack(">Q", len(plaintext)))
        for chunk in chunks:
            enc_chunk = public_key.encrypt(chunk, _OAEP)
            f.write(struct.pack(">I", len(enc_chunk)))
            f.write(enc_chunk)

    return output_path


def decrypt_file(input_path: str, private_key, output_path: str | None = None) -> str:

    if output_path is None:
        base = input_path[:-4] if input_path.endswith(".enc") else input_path
        output_path = base + ".dec"

    with open(input_path, "rb") as f:
        (num_chunks,) = struct.unpack(">I", f.read(4))
        (original_len,) = struct.unpack(">Q", f.read(8))

        plaintext = bytearray()
        for _ in range(num_chunks):
            (chunk_len,) = struct.unpack(">I", f.read(4))
            enc_chunk = f.read(chunk_len)
            plaintext.extend(private_key.decrypt(enc_chunk, _OAEP))

    with open(output_path, "wb") as f:
        f.write(bytes(plaintext[:original_len]))

    return output_path


def benchmark_rsa_vs_rc5(public_key, private_key, data_size_kb: int = 100):
    print(f"--- БЕНЧМАРК (Розмір тестового файлу: {data_size_kb} КБ) ---")

    data = os.urandom(data_size_kb * 1024)

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_data.bin")
        with open(test_file, "wb") as f:
            f.write(data)

        rsa_enc_path = os.path.join(tmpdir, "test_rsa.enc")
        rsa_dec_path = os.path.join(tmpdir, "test_rsa.dec")

        t0 = time.perf_counter()
        encrypt_file(test_file, public_key, rsa_enc_path)
        rsa_enc_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        decrypt_file(rsa_enc_path, private_key, rsa_dec_path)
        rsa_dec_time = time.perf_counter() - t0

        print("\n1. RSA (Лаб 4):")
        print(f"   Час шифрування:    {rsa_enc_time:.4f} сек")
        print(f"   Час розшифрування: {rsa_dec_time:.4f} сек")

        w, r, b = 32, 12, 16
        password = "benchmark_password"

        t0 = time.perf_counter()
        rc5_enc_path = process_file(test_file, password, w, r, b, mode='encrypt')
        rc5_enc_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        process_file(rc5_enc_path, password, w, r, b, mode='decrypt')
        rc5_dec_time = time.perf_counter() - t0

        print("\n2. RC5:")
        print(f"   Час шифрування:    {rc5_enc_time:.4f} сек")
        print(f"   Час розшифрування: {rc5_dec_time:.4f} сек")

        print("\n--- ВИСНОВОК ---")
        if rsa_enc_time < rc5_enc_time:
            ratio = rc5_enc_time / rsa_enc_time if rsa_enc_time > 0 else 0
            print(f"RSA виявився швидшим за RC5 у {ratio:.1f} разів.")
        else:
            ratio = rsa_enc_time / rc5_enc_time if rc5_enc_time > 0 else 0
            print(f"RC5 виявився швидшим за RSA у {ratio:.1f} разів.")

    return {
        "data_kb": data_size_kb,
        "rsa_enc_time": rsa_enc_time,
        "rsa_dec_time": rsa_dec_time,
        "rc5_enc_time": rc5_enc_time,
        "rc5_dec_time": rc5_dec_time,
    }