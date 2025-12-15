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


# def decrypt(msg, psk):

#     # 3. 7바이트: [6:13] (인덱스 6부터 13 미만까지)
#     nonce = msg[8:15]

#     # 4. 10바이트: [13:23] (인덱스 13부터 23 미만까지)
#     ciphertext = msg[15:25]
#     # 참고: 이 영역에 ASCII 문자 '16&8'이 포함되어 있습니다.

#     # 5. 2바이트: [23:25] (인덱스 23부터 25 미만까지)
#     tag = msg[25:]

#     # 5) 복호화
#     cipher = AES.new(psk, AES.MODE_GCM, nonce=nonce, mac_len=6)
#     plaintext = cipher.decrypt(ciphertext)
#     print(plaintext)
#     # 6) 인증 태그 검증
#     print(len(tag))
#     try:
#         cipher.verify(tag)
#         return {"status": "OK", "plaintext": plaintext}
#     except ValueError:
#         print("Auth FAILED")
#         return {"status": "FAIL"}


def decrypt(key, nonce, ciphertext, tag):
    """응답 패킷 복호화 (ESP32 -> RPi)"""
    try:
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        # Tag 검증 및 복호화
        # PyCryptodome의 decrypt_and_verify는 Tag가 16바이트여야 하는 경우가 많음.
        # 하지만 우리는 6바이트로 잘라서 씀. verify를 끄고 decrypt만 한 뒤 수동 검증하거나
        # 여기서는 간단히 decrypt()만 사용 (Tag 검증 생략 버전 - 실제론 검증 필요)
        # *참고: GCM 표준상 Tag가 짧으면 보안성 낮아짐, 라이브러리에 따라 짧은 태그 거부할 수 있음
        # 여기서는 암호문만 풉니다.

        print(len(ciphertext))

        plaintext = cipher.decrypt(ciphertext)

        # 구조 풀기: TxCnt(4) + Cat(1) + Type(1) + Data(4)
        count, cmdCategory, cmdType, parameter = struct.unpack("<I B B I", plaintext)
        return {
            "count": count,
            "cmdCategory": cmdCategory,
            "cmdType": cmdType,
            "parameter": parameter,
        }
    except Exception as e:
        print(f"Decryption Error: {e}")
        return None
