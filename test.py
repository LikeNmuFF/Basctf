cipher_hex = "3f0c0d0f78174f0c4a0a1f0f0f75174e0c1a1f0d"
cipher_bytes = bytes.fromhex(cipher_hex)

for key in range(256):
    plain = bytes(b ^ key for b in cipher_bytes)
    try:
        text = plain.decode()
    except UnicodeDecodeError:
        continue
    if text.startswith("CTF{") and text.endswith("}"):
        print(key, text)
        
    