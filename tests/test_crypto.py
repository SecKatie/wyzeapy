import base64
import unittest

from wyzeapy.crypto import xxtea_decrypt, xxtea_decrypt_b64

# XXTEA "with length" encrypt, matching xxtea-js, used only to build test
# vectors for the decrypt path the library actually uses.
_DELTA = 0x9E3779B9


def _to_uint32(data, include_length):
    n = (len(data) + 3) >> 2
    if include_length:
        v = [0] * (n + 1)
        v[n] = len(data)
    else:
        v = [0] * max(n, 1)
    for i, b in enumerate(data):
        v[i >> 2] |= b << ((i & 3) << 3)
    return v


def _mx(s, y, z, p, e, k):
    return (
        (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)))
        ^ ((s ^ y) + (k[(p & 3) ^ e] ^ z))
    ) & 0xFFFFFFFF


def xxtea_encrypt(data, key):
    if not data:
        return data
    if len(key) < 16:
        key = key + b"\x00" * (16 - len(key))
    v = _to_uint32(data, True)
    k = _to_uint32(key, False)
    n = len(v)
    last = n - 1
    z = v[last]
    s = 0
    q = 6 + 52 // n
    for _ in range(q):
        s = (s + _DELTA) & 0xFFFFFFFF
        e = (s >> 2) & 3
        for p in range(last):
            y = v[p + 1]
            v[p] = (v[p] + _mx(s, y, z, p, e, k)) & 0xFFFFFFFF
            z = v[p]
        y = v[0]
        v[last] = (v[last] + _mx(s, y, z, last, e, k)) & 0xFFFFFFFF
        z = v[last]
    out = bytearray(len(v) * 4)
    for i in range(len(v)):
        out[i * 4] = v[i] & 0xFF
        out[i * 4 + 1] = (v[i] >> 8) & 0xFF
        out[i * 4 + 2] = (v[i] >> 16) & 0xFF
        out[i * 4 + 3] = (v[i] >> 24) & 0xFF
    return bytes(out)


class TestXXTEA(unittest.TestCase):
    def test_roundtrip(self):
        key = b"a-test-access-token"
        for text in [b"", b"x", b"secret-key", b"ME_WCO3_80482CD5A6F26ulFdkMWgjuk"]:
            ct = xxtea_encrypt(text, key)
            self.assertEqual(xxtea_decrypt(ct, key), text)

    def test_decrypt_b64_roundtrip(self):
        key = "token123"
        b64 = base64.b64encode(xxtea_encrypt(b"hello world", key.encode())).decode()
        self.assertEqual(xxtea_decrypt_b64(b64, key), "hello world")

    def test_decrypt_b64_passthrough_on_empty(self):
        # Mirrors the web app: empty value or key returns the value unchanged.
        self.assertEqual(xxtea_decrypt_b64("", "key"), "")
        self.assertEqual(xxtea_decrypt_b64("abc", ""), "abc")

    def test_stream_key_wire_format(self):
        """Wyze's lake get-streams delivers the Agora key/salt XXTEA-encrypted
        with the account access token: the key is a 32-char AES key string and
        the salt is base64 of exactly 32 bytes. Uses a synthetic token and
        synthetic (but correctly shaped) values — no real credentials."""
        token = "synthetic-access-token-for-tests"
        plain_key = "ME_WCO3_0123456789ABCDEF01234567"  # 32-char AES key
        plain_salt_b64 = base64.b64encode(bytes(range(32))).decode()  # 32 bytes

        enc_key = base64.b64encode(
            xxtea_encrypt(plain_key.encode(), token.encode())
        ).decode()
        enc_salt = base64.b64encode(
            xxtea_encrypt(plain_salt_b64.encode(), token.encode())
        ).decode()

        key = xxtea_decrypt_b64(enc_key, token)
        salt_b64 = xxtea_decrypt_b64(enc_salt, token)

        self.assertEqual(key, plain_key)
        self.assertEqual(len(key), 32)
        self.assertEqual(len(base64.b64decode(salt_b64)), 32)


if __name__ == "__main__":
    unittest.main()
