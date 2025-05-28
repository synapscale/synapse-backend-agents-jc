import jwt
from datetime import datetime, timedelta

payload = {
    'sub': 'demo_user_123',
    'username': 'demo@example.com',
    'role': 'user', 
    'scopes': ['files:read', 'files:write', 'llm:use'],
    'exp': datetime.utcnow() + timedelta(minutes=60)
}

secret = 'insecure_key_for_dev_only_please_change_in_production'
token = jwt.encode(payload, secret, algorithm='HS256')

print('Token de teste:')
print(token)
