import os
import struct
from Crypto.Cipher import AES


def encrypt(key, req_count, cmdCategory, cmdType, parameter):
    nonce = os.urandom(7)

    # [핵심 변경counter] 10바이트 구조체 생성 (Little Endian)
    # Counter(4) + Cat(1) + Type(1) + Param(4) = 10 Bytes
    # '<I B B I' 형식 문자열 의미:
    # < : Little Endian
    # I : unsigned int (4 bytes)
    # B : unsigned char (1 byte)
    plain_data = struct.pack("<I B B I", req_count, cmdCategory, cmdType, parameter)

    print(f"[*] Payload Hex: {plain_data.hex()}")

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, full_tag = cipher.encrypt_and_digest(plain_data)
    tag = full_tag[:6]

    print("counter", req_count)
    print("nonce", nonce)
    print("ciphertext", ciphertext)
    print("nonctage", tag)

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
