#!/usr/bin/env python3
"""
Gerador de chaves seguras para SynapScale Backend
Gera todas as chaves necessárias para configuração segura
"""

import secrets
import base64
import string
import os
from pathlib import Path

def generate_secret_key(length=32):
    """Gera uma chave secreta segura usando caracteres alfanuméricos e símbolos"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_url_safe_token(length=32):
    """Gera um token seguro URL-safe"""
    return secrets.token_urlsafe(length)

def generate_encryption_key():
    """Gera uma chave de criptografia de 32 bytes em base64"""
    key_bytes = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(key_bytes).decode()

def generate_database_password(length=16):
    """Gera uma senha segura para banco de dados"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 GERADOR DE CHAVES SEGURAS - SYNAPSCALE BACKEND")
    print("=" * 60)
    
    # Gerar todas as chaves necessárias
    keys = {
        'SECRET_KEY': generate_secret_key(64),
        'JWT_SECRET_KEY': generate_url_safe_token(64),
        'ENCRYPTION_KEY': generate_encryption_key(),
        'POSTGRES_PASSWORD': generate_database_password(20),
        'REDIS_PASSWORD': generate_database_password(16),
    }
    
    print("\n🔑 CHAVES GERADAS:")
    print("-" * 40)
    
    # Exibir chaves geradas
    for key_name, key_value in keys.items():
        print(f"{key_name}={key_value}")
    
    print("\n" + "=" * 60)
    print("📋 INSTRUÇÕES:")
    print("1. Copie as chaves acima para seu arquivo .env")
    print("2. NUNCA commite essas chaves no git")
    print("3. Use chaves diferentes para cada ambiente (dev/prod)")
    print("4. Armazene chaves de produção em um gerenciador seguro")
    
    # Opção de salvar em arquivo .env
    save_to_file = input("\n💾 Salvar chaves em arquivo .env? (s/N): ").lower().strip()
    
    if save_to_file == 's':
        env_file = Path('.env')
        
        if env_file.exists():
            backup = input("⚠️  Arquivo .env já existe. Fazer backup? (S/n): ").lower().strip()
            if backup != 'n':
                backup_name = f".env.backup.{secrets.token_hex(4)}"
                env_file.rename(backup_name)
                print(f"✅ Backup salvo como: {backup_name}")
        
        # Criar novo arquivo .env
        with open('.env', 'w') as f:
            f.write("# ==============================================================================\n")
            f.write("# SYNAPSCALE BACKEND - VARIÁVEIS DE AMBIENTE\n")
            f.write("# GERADO AUTOMATICAMENTE - NÃO COMMITAR NO GIT\n")
            f.write("# ==============================================================================\n\n")
            
            f.write("# Configurações básicas\n")
            f.write("ENVIRONMENT=development\n")
            f.write("DEBUG=true\n\n")
            
            f.write("# Chaves de segurança\n")
            for key_name, key_value in keys.items():
                f.write(f"{key_name}={key_value}\n")
            
            f.write("\n# Banco de dados\n")
            f.write(f"DATABASE_URL=postgresql://postgres:{keys['POSTGRES_PASSWORD']}@localhost:5432/synapse\n")
            f.write(f"POSTGRES_USER=postgres\n")
            f.write(f"POSTGRES_DB=synapse\n\n")
            
            f.write("# Redis\n")
            f.write("REDIS_URL=redis://localhost:6379/0\n\n")
            
            f.write("# APIs de IA (configure conforme necessário)\n")
            f.write("OPENAI_API_KEY=\n")
            f.write("ANTHROPIC_API_KEY=\n")
            f.write("GEMINI_API_KEY=\n")
            f.write("MISTRAL_API_KEY=\n\n")
            
            f.write("# Email (configure conforme necessário)\n")
            f.write("SMTP_HOST=\n")
            f.write("SMTP_PORT=587\n")
            f.write("SMTP_USERNAME=\n")
            f.write("SMTP_PASSWORD=\n")
            f.write("SMTP_USE_TLS=true\n")
        
        print(f"✅ Arquivo .env criado com chaves seguras!")
        print("📝 Configure as APIs e SMTP conforme necessário")
    
    print("\n🛡️  LEMBRETE DE SEGURANÇA:")
    print("- Use diferentes chaves para desenvolvimento e produção")
    print("- Armazene chaves de produção em cofres seguros (AWS Secrets, etc)")
    print("- Rode 'python security_scan.py' regularmente")
    print("- Monitore logs para tentativas de acesso não autorizadas")

if __name__ == "__main__":
    main()
