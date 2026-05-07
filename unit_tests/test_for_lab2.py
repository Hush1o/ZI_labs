import unittest

from labs.lab2 import MD5, get_string_hash


class TestMD5(unittest.TestCase):

    def test_empty_string(self):
        self.assertEqual(
            get_string_hash(""),
            "d41d8cd98f00b204e9800998ecf8427e"
        )

    def test_single_char(self):
        self.assertEqual(
            get_string_hash("a"),
            "0cc175b9c0f1b6a831c399e269772661"
        )

    def test_abc_string(self):
        self.assertEqual(
            get_string_hash("abc"),
            "900150983cd24fb0d6963f7d28e17f72"
        )

    def test_message_digest(self):
        text = "message digest"
        self.assertEqual(
            get_string_hash(text),
            "f96b697d7cb7938d525a2f31aaf161d0"
        )

    def test_all_letter(self):
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        self.assertEqual(
            get_string_hash(text),
            "d174ab98d277d9f5a5611c2c9f419d9f"
        )

if __name__ == '__main__':
    unittest.main()