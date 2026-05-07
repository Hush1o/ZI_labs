import unittest
import os
import sys
import tempfile
from labs import lab1, lab2
from labs.lab3 import RC5, process_file


class TestRC5(unittest.TestCase):

    def test_encrypt_decrypt_roundtrip(self):
        rc5 = RC5(32, 12, bytes(range(16)))
        block = b"ABCDEFGH"
        self.assertEqual(rc5.decrypt_block(rc5.encrypt_block(block)), block)

    def test_different_keys_different_ciphertext(self):
        block = os.urandom(8)
        ct1 = RC5(32, 12, bytes(16)).encrypt_block(block)
        ct2 = RC5(32, 12, bytes([1] * 16)).encrypt_block(block)
        self.assertNotEqual(ct1, ct2)

    def test_subkey_table_length(self):
        rc5 = RC5(32, 12, bytes(16))
        self.assertEqual(len(rc5.S), 2 * 12 + 2)

    def test_process_file_encrypt_decrypt(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "file.txt")
            with open(src, 'wb') as f:
                f.write(b"test data 1234")
            enc = process_file(src, "password", 32, 12, 16, mode='encrypt')
            dec = process_file(enc, "password", 32, 12, 16, mode='decrypt')
            with open(dec, 'rb') as f:
                self.assertEqual(f.read(), b"test data 1234")

    def test_wrong_password_raises(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "file.txt")
            with open(src, 'wb') as f:
                f.write(b"secret message!")
            enc = process_file(src, "correct", 32, 12, 16, mode='encrypt')
            with self.assertRaises(Exception):
                process_file(enc, "wrong", 32, 12, 16, mode='decrypt')


if __name__ == "__main__":
    unittest.main(verbosity=2)