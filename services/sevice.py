import os
from Crypto.Cipher import AES


def encrypt(plaintext, psk):

    nonce = os.urandom(7)

    cipher = AES.new(psk, AES.MODE_GCM, nonce=nonce, mac_len=6)

    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    print("Ciphertext :", ciphertext.hex(), "len =", len(ciphertext))  # 10B
    print("Auth Tag   :", tag[:6].hex(), "len =", 6)

    return {"ciphertext": ciphertext, "tag": tag, "nonce": nonce}
