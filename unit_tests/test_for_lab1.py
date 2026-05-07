import unittest
import labs.lab1
from labs import lab1

class TestLab1(unittest.TestCase):

    def test_generate_n_sequence(self):
        seq = lab1.generate_n_sequence(100)
        for num in seq:
            self.assertTrue(0 <= num < lab1.m)

    def test_gcd (self) :
        self.assertEqual(lab1.gcd(9, 81), 9)
        self.assertEqual(lab1.gcd(72, 152), 8)
        self.assertEqual(lab1.gcd(33, 96), 3)

    def test_lemer_generator(self):
        sequence = lab1.generate_N_sequence(1, start=11)
        self.assertEqual(sequence[0], 19995)

if __name__ == '__main__':
    unittest.main()