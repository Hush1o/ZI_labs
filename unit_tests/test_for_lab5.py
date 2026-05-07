import unittest
import os
import tempfile

from labs.lab5 import (
    generate_keys,
    save_private_key,
    save_public_key,
    load_private_key,
    load_public_key,
    sign_message,
    verify_message,
    sign_file,
    verify_file,
)


class TestDSSSignature(unittest.TestCase):

    def test_generate_keys(self):
        private_key, public_key = generate_keys(key_size=2048)

        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertEqual(private_key.key_size, 2048)

    def test_save_and_load_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            priv_path = os.path.join(tmpdir, "dsa_priv.pem")
            pub_path  = os.path.join(tmpdir, "dsa_pub.pem")

            orig_priv, orig_pub = generate_keys(2048)

            save_private_key(orig_priv, priv_path)
            save_public_key(orig_pub, pub_path)

            self.assertTrue(os.path.exists(priv_path))
            self.assertTrue(os.path.exists(pub_path))

            loaded_priv = load_private_key(priv_path)
            loaded_pub  = load_public_key(pub_path)

            self.assertEqual(
                orig_priv.private_numbers().x,
                loaded_priv.private_numbers().x,
            )
            self.assertEqual(
                orig_pub.public_numbers().y,
                loaded_pub.public_numbers().y,
            )

    def test_sign_and_verify_message(self):
        private_key, public_key = generate_keys(2048)
        message = "Захист інформації — тестове повідомлення"

        signature = sign_message(private_key, message)

        self.assertIsInstance(signature, bytes)
        self.assertGreater(len(signature), 0)
        self.assertTrue(verify_message(public_key, message, signature))

    def test_verify_tampered_message(self):
        private_key, public_key = generate_keys(2048)
        message = "Оригінальне повідомлення"

        signature = sign_message(private_key, message)

        self.assertFalse(verify_message(public_key, message + "!", signature))

    def test_sign_and_verify_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "document.txt")
            sig_path  = os.path.join(tmpdir, "document.sig")

            with open(file_path, "w") as f:
                f.write("Тестовий документ для цифрового підпису.\n" * 50)

            private_key, public_key = generate_keys(2048)

            sign_file(private_key, file_path, sig_path)
            self.assertTrue(os.path.exists(sig_path))

            self.assertTrue(verify_file(public_key, file_path, sig_path))

            with open(file_path, "a") as f:
                f.write("(змінено після підпису)\n")

            self.assertFalse(verify_file(public_key, file_path, sig_path))


if __name__ == "__main__":
    unittest.main()