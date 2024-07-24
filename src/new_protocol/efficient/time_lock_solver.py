from Crypto.Cipher import ChaCha20
import time

class TimeLockSolver:
    def __init__(self, n, a, t, CK, CM, nonce) -> None:
        self.n = n
        self.a = a
        self.t = t
        self.CK = CK
        self.CM = CM
        self.nonce = nonce

    def unlock(self):
        first_time = time.perf_counter()
        nonce = int.to_bytes(self.nonce, length=8)
        ciphertext = int.to_bytes(self.CM, length=32)
        x = self.a
        for _ in range(1, self.t+1):
            x = (x**2) % self.n
        b = x
        second_time = time.perf_counter()
        print(f"time taken: {second_time-first_time}")
        K = int.to_bytes(self.CK - b, length=32)
        cipher = ChaCha20.new(key=K, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        return int.from_bytes(plaintext)
