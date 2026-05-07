import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from labs.lab4 import (
    generate_key_pair,
    save_private_key,
    save_public_key,
    load_private_key,
    load_public_key,
    encrypt_file,
    decrypt_file,
)

@pytest.fixture
def keys():
    return generate_key_pair(2048)

def test_generate_keys_returns_pair():
    _, pub = generate_key_pair(2048)
    assert _ is not None
    assert pub is not None

def test_encrypt_decrypt_file(keys, tmp_path):
    _, pub = keys
    file_path = tmp_path / "test.txt"
    file_path.write_text("secret message")
    enc_path = encrypt_file(str(file_path), pub)
    dec_path = decrypt_file(enc_path, _)
    with open(dec_path, "rb") as f:
        assert f.read() == b"secret message"

def test_encrypt_decrypt_large_file(keys, tmp_path):
    _, pub = keys
    file_path = tmp_path / "large.bin"
    data = os.urandom(500)
    file_path.write_bytes(data)
    enc_path = encrypt_file(str(file_path), pub)
    dec_path = decrypt_file(enc_path, _)
    with open(dec_path, "rb") as f:
        assert f.read() == data

def test_encrypt_creates_enc_file(keys, tmp_path):
    _, pub = keys
    file_path = tmp_path / "test.txt"
    file_path.write_text("data")
    enc_path = encrypt_file(str(file_path), pub)
    assert enc_path.endswith(".enc")
    assert os.path.exists(enc_path)

def test_decrypt_creates_dec_file(keys, tmp_path):
    _, pub = keys
    file_path = tmp_path / "test.txt"
    file_path.write_text("data")
    enc_path = encrypt_file(str(file_path), pub)
    dec_path = decrypt_file(enc_path, _)
    assert dec_path.endswith(".dec")
    assert os.path.exists(dec_path)

def test_save_load_private_key_no_password(keys, tmp_path):
    _, _ = keys
    path = str(tmp_path / "priv.pem")
    save_private_key(_, path)
    loaded = load_private_key(path)
    assert loaded is not None

def test_save_load_private_key_with_password(keys, tmp_path):
    _, _ = keys
    path = str(tmp_path / "priv_enc.pem")
    save_private_key(_, path, key_phrase=b"secret")
    loaded = load_private_key(path, key_phrase=b"secret")
    assert loaded is not None

def test_save_load_public_key(keys, tmp_path):
    _, pub = keys
    path = str(tmp_path / "pub.pem")
    save_public_key(pub, path)
    loaded = load_public_key(path)
    assert loaded is not None

def test_encrypt_custom_output_path(keys, tmp_path):
    _, pub = keys
    file_path = tmp_path / "test.txt"
    file_path.write_text("custom output")
    enc_path = str(tmp_path / "custom.enc")
    result = encrypt_file(str(file_path), pub, enc_path)
    assert result == enc_path
    assert os.path.exists(enc_path)

def test_decrypt_custom_output_path(keys, tmp_path):
    _, pub = keys
    file_path = tmp_path / "test.txt"
    file_path.write_text("custom output")
    enc_path = encrypt_file(str(file_path), pub)
    dec_path = str(tmp_path / "custom.dec")
    result = decrypt_file(enc_path, _, dec_path)
    assert result == dec_path
    assert os.path.exists(dec_path)

def test_encrypt_decrypt_empty_file(keys, tmp_path):
    _, pub = keys
    file_path = tmp_path / "empty.txt"
    file_path.write_bytes(b"")
    enc_path = encrypt_file(str(file_path), pub)
    dec_path = decrypt_file(enc_path, _)
    with open(dec_path, "rb") as f:
        assert f.read() == b""

def test_benchmark_returns_dict(keys):
    from labs.lab4 import benchmark_rsa_vs_rc5
    _, pub = keys
    result = benchmark_rsa_vs_rc5(pub, _, data_size_kb=1)
    assert "rsa_enc_time" in result
    assert "rsa_dec_time" in result
    assert "rc5_enc_time" in result
    assert "rc5_dec_time" in result
    assert result["data_kb"] == 1