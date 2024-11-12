import secrets
import string

def generate_token(length=32):
    # Определяем символы для генерации токена
    alphabet = string.ascii_letters + string.digits
    # Генерируем случайный токен заданной длины
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token

