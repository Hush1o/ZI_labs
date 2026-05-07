import struct
import math

class MD5:
    def __init__(self):
        self.A = 0x67452301
        self.B = 0xEFCDAB89
        self.C = 0x98BADCFE
        self.D = 0x10325476
        self._count = 0
        self._buffer = b""
        self._T = [int(4294967296 * abs(math.sin(i + 1))) & 0xFFFFFFFF for i in range(64)]
        self._S = [7, 12, 17, 22] * 4 + [5, 9, 14, 20] * 4 + [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4

    def _left_rotate(self, x, n):
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

    def _process(self, chunk):
        X = list(struct.unpack("<16I", chunk))
        a, b, c, d = self.A, self.B, self.C, self.D
        for i in range(64):
            # if i == 0 or i % 16 == 0:
            #     print(f"A={hex(a)}, B={hex(b)}, C={hex(c)}, D={hex(d)}")
            #     print(f"A={bin(a)}, B={bin(b)}, C={bin(c)}, D={bin(d)}")
            #     print(f"A={a}, B={b}, C={c}, D={d}")
            #     print("-"*145)
            if i < 16:
                f = (b & c) | ((~b) & d)
                g = i
            elif i < 32:
                f = (d & b) | ((~d) & c)
                g = (5 * i + 1) % 16
            elif i < 48:
                f = b ^ c ^ d
                g = (3 * i + 5) % 16
            else:
                f = c ^ (b | (~d))
                g = (7 * i) % 16
            temp = (a + (f & 0xFFFFFFFF) + self._T[i] + X[g]) & 0xFFFFFFFF
            temp = self._left_rotate(temp, self._S[i])
            a, b, c, d = d, (b + temp) & 0xFFFFFFFF, b, c
        self.A = (self.A + a) & 0xFFFFFFFF
        self.B = (self.B + b) & 0xFFFFFFFF
        self.C = (self.C + c) & 0xFFFFFFFF
        self.D = (self.D + d) & 0xFFFFFFFF

    def update(self, data):
        self._count += len(data)
        self._buffer += data
        while len(self._buffer) >= 64:
            self._process(self._buffer[:64])
            self._buffer = self._buffer[64:]

    def finalize(self):
        msg = self._buffer + b'\x80'
        while len(msg) % 64 != 56:
            msg += b'\x00'
        msg += struct.pack("<Q", self._count * 8)
        for i in range(0, len(msg), 64):
            self._process(msg[i:i + 64])
        return struct.pack("<4I", self.A, self.B, self.C, self.D).hex()

def get_string_hash(text):
    m = MD5()
    m.update(text.encode('utf-8'))
    return m.finalize()

def get_file_hash(path):
    m = MD5()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            m.update(chunk)
    return m.finalize()

def verify_file_integrity(path, expected):
    if not expected: return False
    actual = get_file_hash(path)
    return actual.lower() == expected.strip().lower()