#!/usr/bin/env python3
"""
Script para descriptografar dados que já foram criptografados no banco
Identifica dados criptografados e os descriptografa para texto claro
"""
import os
import sys
import base64
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

# Adicionar src ao path
sys.path.insert(0, 'src')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from synapse.models.user_variable import UserVariable

def is_base64_encoded(value: str) -> bool:
    """
    Verifica se um valor parece ser Base64 encoded
    """
    try:
        # Valores Base64 têm padrões específicos
        if len(value) < 10:
            return False
        
        # Base64 típico tem múltiplos de 4 caracteres ou com padding
        if len(value) % 4 == 0 or value.endswith('='):
            # Tentar decodificar
            decoded = base64.b64decode(value)
            # Se conseguiu decodificar e tem tamanho razoável, provavelmente é Base64
            if len(decoded) > 5:
                return True
    except:
        pass
    
    return False

def is_fernet_encrypted(value: str) -> bool:
    """
    Verifica se um valor parece ser encrypted com Fernet
    Fernet produz strings Base64 que começam com padrões específicos
    """
    if not value:
        return False
    
    # Valores Fernet são Base64 e têm tamanhos específicos
    if is_base64_encoded(value):
        try:
            decoded = base64.b64decode(value)
            # Fernet tokens têm tamanhos específicos (pelo menos 57 bytes)
            if len(decoded) >= 57:
                return True
        except:
            pass
    
    return False

def attempt_fernet_decrypt(encrypted_value: str) -> str:
    """
    Tenta descriptografar usando chaves Fernet conhecidas ou padrão
    """
    encryption_key = os.getenv("ENCRYPTION_KEY", "")
    
    if not encryption_key:
        # Tentar algumas chaves padrão comuns
        common_keys = [
            "GERE_UMA_CHAVE_CRIPTOGRAFIA_BASE64_32_BYTES",
            "dummy_key_for_testing_32_bytes_long",
        ]
    else:
        common_keys = [encryption_key]
    
    for key in common_keys:
        try:
            if len(key) < 32:
                # Expandir chave pequena para 32 bytes
                key = (key + "0" * 32)[:32]
            
            key_bytes = key.encode('utf-8')[:32]
            key_b64 = base64.b64encode(key_bytes).decode('utf-8')
            
            # Tentar usar cryptography se estiver disponível
            try:
                from cryptography.fernet import Fernet
                f = Fernet(key_b64)
                decrypted = f.decrypt(encrypted_value.encode()).decode()
                return decrypted
            except ImportError:
                # Se cryptography não está instalada, não podemos descriptografar
                continue
            except Exception:
                continue
                
        except Exception:
            continue
    
    return encrypted_value  # Retornar original se não conseguir descriptografar

def decrypt_all_variables():
    """
    Descriptografa todas as variáveis que parecem estar criptografadas
    """
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        print("🔍 Buscando variáveis que parecem estar criptografadas...")
        
        # Buscar todas as variáveis
        all_vars = db.query(UserVariable).all()
        
        encrypted_vars = []
        
        for var in all_vars:
            if is_fernet_encrypted(var.value):
                encrypted_vars.append(var)
        
        print(f"📊 Encontradas {len(encrypted_vars)} variáveis que parecem estar criptografadas")
        
        if len(encrypted_vars) == 0:
            print("✅ Nenhuma variável criptografada detectada!")
            return True
        
        # Mostrar algumas para confirmar
        print("\n📋 Primeiras 5 variáveis encontradas:")
        for i, var in enumerate(encrypted_vars[:5]):
            print(f"   {i+1}. {var.key} = {var.value[:30]}{'...' if len(var.value) > 30 else ''}")
        
        # Confirmar antes de descriptografar
        resposta = input(f"\n🔧 Deseja tentar descriptografar todas as {len(encrypted_vars)} variáveis? (s/N): ")
        
        if resposta.lower() != 's':
            print("❌ Operação cancelada pelo usuário")
            return False
        
        print("🔄 Descriptografando variáveis...")
        
        success_count = 0
        failed_count = 0
        
        for var in encrypted_vars:
            try:
                original_value = var.value
                decrypted_value = attempt_fernet_decrypt(original_value)
                
                if decrypted_value != original_value:
                    # Conseguiu descriptografar
                    var.value = decrypted_value
                    var.is_encrypted = False
                    success_count += 1
                    print(f"   ✅ {var.key}: descriptografado com sucesso")
                else:
                    # Não conseguiu descriptografar
                    failed_count += 1
                    print(f"   ❌ {var.key}: falha ao descriptografar")
                    
            except Exception as e:
                failed_count += 1
                print(f"   ❌ {var.key}: erro: {e}")
        
        if success_count > 0:
            # Salvar mudanças
            db.commit()
            print(f"\n✅ {success_count} variáveis descriptografadas com sucesso!")
            
        if failed_count > 0:
            print(f"⚠️  {failed_count} variáveis não puderam ser descriptografadas")
            print("💡 Essas variáveis podem ter sido criptografadas com uma chave diferente")
        
        # Verificação final
        remaining = 0
        for var in db.query(UserVariable).all():
            if is_fernet_encrypted(var.value):
                remaining += 1
        
        if remaining == 0:
            print("🎉 TODAS AS VARIÁVEIS FORAM DESCRIPTOGRAFADAS!")
        else:
            print(f"⚠️  Ainda restam {remaining} variáveis criptografadas")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        return False

def main():
    print("🔐 SCRIPT DE DESCRIPTOGRAFIA DE VARIÁVEIS")
    print("=" * 60)
    print("Este script identifica e descriptografa variáveis que foram")
    print("criptografadas anteriormente no banco de dados.")
    print("=" * 60)
    
    success = decrypt_all_variables()
    
    if success:
        print("\n🎉 Script executado com sucesso!")
        print("💡 As variáveis agora estão em texto claro no banco.")
    else:
        print("\n❌ Script falhou!")

if __name__ == "__main__":
    main() 