import struct
import os
from labs import lab1, lab2


class RC5:
    def __init__(self, w, r, key):
        self.w = w
        self.r = r
        self.b = len(key)
        self.u = w // 8
        self.c = max(1, (self.b + self.u - 1) // self.u)
        self.mod = 1 << self.w
        self.mask = self.mod - 1
        self.S = self._expand_key(key)

    def _rotate_left(self, val, n):
        n %= self.w
        return ((val << n) & self.mask) | (val >> (self.w - n))

    def _rotate_right(self, val, n):
        n %= self.w
        return (val >> n) | ((val << (self.w - n)) & self.mask)

    def _expand_key(self, key):
        RC5_CONSTANTS = {
            16: (0xB7E1, 0x9E37),
            32: (0xB7E15163, 0x9E3779B9),
            64: (0xB7E15162_8AED2A6B, 0x9E3779B9_7F4A7C15),
        }
        P, Q = RC5_CONSTANTS[self.w]

        L = [0] * self.c
        for i in range(self.b):
            L[i // self.u] += key[i] << (8 * (i % self.u))

        t = 2 * self.r + 2
        S = [0] * t
        S[0] = P
        for i in range(1, t):
            S[i] = (S[i - 1] + Q) & self.mask

        i = j = A = B = 0
        for _ in range(3 * max(self.c, t)):
            A = S[i] = self._rotate_left((S[i] + A + B) & self.mask, 3)
            B = L[j] = self._rotate_left((L[j] + A + B) & self.mask, (A + B) % self.w)
            i = (i + 1) % t
            j = (j + 1) % self.c
        return S

    def encrypt_block(self, data):
        fmt = {16: '<2H', 32: '<2I', 64: '<2Q'}[self.w]
        A, B = struct.unpack(fmt, data)
        A = (A + self.S[0]) & self.mask
        B = (B + self.S[1]) & self.mask
        for i in range(1, self.r + 1):
            A = (self._rotate_left(A ^ B, B % self.w) + self.S[2 * i]) & self.mask
            B = (self._rotate_left(B ^ A, A % self.w) + self.S[2 * i + 1]) & self.mask
        return struct.pack(fmt, A, B)

    def decrypt_block(self, data):
        fmt = {16: '<2H', 32: '<2I', 64: '<2Q'}[self.w]
        A, B = struct.unpack(fmt, data)
        for i in range(self.r, 0, -1):
            B = self._rotate_right((B - self.S[2 * i + 1]) & self.mask, A % self.w) ^ A
            A = self._rotate_right((A - self.S[2 * i]) & self.mask, B % self.w) ^ B
        B = (B - self.S[1]) & self.mask
        A = (A - self.S[0]) & self.mask
        return struct.pack(fmt, A, B)


def process_file(path, password, w, r, b, mode='encrypt'):
    h = lab2.get_string_hash(password)
    key = bytes.fromhex(h)[:b]

    cipher = RC5(w, r, key)
    block_size = (2 * w) // 8

    if mode == 'encrypt':
        with open(path, 'rb') as f:
            data = f.read()

        iv_seq = lab1.generate_N_sequence(block_size)
        iv = bytes([x % 256 for x in iv_seq])

        encrypted_iv = cipher.encrypt_block(iv)

        pad_len = block_size - (len(data) % block_size)
        data += bytes([pad_len] * pad_len)

        result = encrypted_iv
        prev_block = iv
        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]
            xored = bytes(x ^ y for x, y in zip(block, prev_block))
            encrypted_block = cipher.encrypt_block(xored)
            result += encrypted_block
            prev_block = encrypted_block

        out_path = path + ".rc5"

    else:
        if not path.endswith(".rc5"):
            raise ValueError("Файл для дешифрування повинен мати розширення .rc5")

        with open(path, 'rb') as f:
            data = f.read()

        if len(data) < 2 * block_size:
            raise ValueError("Файл пошкоджений або занадто малий")

        encrypted_iv = data[:block_size]
        iv = cipher.decrypt_block(encrypted_iv)

        result = b""
        prev_block = iv
        for i in range(block_size, len(data), block_size):
            encrypted_block = data[i:i + block_size]
            decrypted = cipher.decrypt_block(encrypted_block)
            result += bytes(x ^ y for x, y in zip(decrypted, prev_block))
            prev_block = encrypted_block

        if len(result) == 0:
            raise ValueError("Дешифрований файл порожній")
        pad_len = result[-1]
        if pad_len == 0 or pad_len > block_size:
            raise ValueError("Невірний padding — можливо хибний пароль")
        result = result[:-pad_len]

        out_path = path[:-4] + ".dec"

    with open(out_path, 'wb') as f:
        f.write(result)
    return out_path