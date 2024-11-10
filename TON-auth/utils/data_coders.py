from cryptography.fernet import Fernet

from config_reader import config

cipher = Fernet(config.cipher_key.get_secret_value())

def encrypt(user_id: int) -> str:
    encrypted_user_id = cipher.encrypt(str(user_id).encode('utf-8'))
    return encrypted_user_id.decode()

def decrypt(encrypted_user_id: str) -> int:
    decrypted_user_id = cipher.decrypt(encrypted_user_id).decode('utf-8')
    try:
        return int(decrypted_user_id)
    except ValueError:
        raise ValueError('Invalid data')
