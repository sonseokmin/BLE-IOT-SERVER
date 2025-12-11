import os
from Crypto.Cipher import AES


def encrypt(plaintext, psk):

    nonce = os.urandom(7)

    cipher = AES.new(psk, AES.MODE_GCM, nonce=nonce, mac_len=6)

    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    print("Ciphertext :", ciphertext.hex(), "len =", len(ciphertext))  # 10B
    print("Auth Tag   :", tag[:6].hex(), "len =", 6)

    return {"ciphertext": ciphertext, "tag": tag, "nonce": nonce}


def decrypt(msg, psk):

    # 3. 7바이트: [6:13] (인덱스 6부터 13 미만까지)
    nonce = msg[6:13]

    # 4. 10바이트: [13:23] (인덱스 13부터 23 미만까지)
    ciphertext = msg[13:23]
    # 참고: 이 영역에 ASCII 문자 '16&8'이 포함되어 있습니다.

    # 5. 2바이트: [23:25] (인덱스 23부터 25 미만까지)
    tag = msg[23:29]

    # 5) 복호화
    cipher = AES.new(psk, AES.MODE_GCM, nonce=nonce, mac_len=6)
    plaintext = cipher.decrypt(ciphertext)
    print(plaintext)
    # 6) 인증 태그 검증
    try:
        cipher.verify(tag)
        return {"status": "OK", "plaintext": plaintext}
    except ValueError:
        print("Auth FAILED")
        return {"status": "FAIL"}
