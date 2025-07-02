#!/usr/bin/env python3
"""
🚨🚨🚨 SCRIPT EXTREMAMENTE PERIGOSO - LEIA ANTES DE EXECUTAR 🚨🚨🚨

⚠️⚠️⚠️ ATENÇÃO: ESTE SCRIPT MANIPULA DIRETAMENTE O BANCO DE DADOS ⚠️⚠️⚠️

🔴 ESTE SCRIPT:
- Conecta DIRETAMENTE ao banco de dados PostgreSQL
- BYPASSA todas as validações da aplicação
- CRIA usuários SEM passar pela API
- PODE CAUSAR INCONSISTÊNCIAS nos dados
- PODE QUEBRAR a integridade referencial
- É PERIGOSO em ambiente de PRODUÇÃO

🛑 SÓ USE ESTE SCRIPT SE:
- Você é um DBA experiente
- A API está quebrada e você precisa criar usuário de emergência
- Você entende os riscos de manipulação direta do banco
- Você fez BACKUP do banco antes

💡 ALTERNATIVAS SEGURAS:
- Use create_saas_user.py (via API)
- Use a interface web da aplicação
- Use endpoints de administração

⚡ AMBIENTES PERIGOSOS:
- Produção (NUNCA use sem backup)
- Staging com dados importantes
- Qualquer ambiente compartilhado
"""

import psycopg2
import uuid
from datetime import datetime
import bcrypt
import os
import sys
from dotenv import load_dotenv

# Cores para terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

load_dotenv()


def show_danger_warning():
    """Mostra avisos de perigo antes de executar"""
    print(f"\n{Colors.RED}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}🚨🚨🚨 PERIGO EXTREMO - MANIPULAÇÃO DIRETA DO BANCO 🚨🚨🚨{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}{'='*80}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  ESTE SCRIPT VAI:{Colors.END}")
    print(f"{Colors.RED}   - Conectar DIRETAMENTE ao banco PostgreSQL{Colors.END}")
    print(f"{Colors.RED}   - CRIAR usuário SEM validações da aplicação{Colors.END}")
    print(f"{Colors.RED}   - BYPASSAR toda a lógica de negócio{Colors.END}")
    print(f"{Colors.RED}   - MODIFICAR dados em produção{Colors.END}")
    
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}🛑 RISCOS:{Colors.END}")
    print(f"{Colors.RED}   - Inconsistência de dados{Colors.END}")
    print(f"{Colors.RED}   - Quebra de integridade referencial{Colors.END}")
    print(f"{Colors.RED}   - Problemas de sincronização{Colors.END}")
    print(f"{Colors.RED}   - Corrupção do sistema{Colors.END}")

def get_environment_info():
    """Detecta informações do ambiente"""
    db_host = os.getenv("DB_HOST", "unknown")
    db_name = os.getenv("DB_NAME", "unknown")
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}🔍 INFORMAÇÕES DO AMBIENTE:{Colors.END}")
    print(f"{Colors.CYAN}   Host: {Colors.WHITE}{db_host}{Colors.END}")
    print(f"{Colors.CYAN}   Database: {Colors.WHITE}{db_name}{Colors.END}")
    
    # Detectar se é produção
    is_production = any([
        "prod" in db_host.lower(),
        "production" in db_host.lower(),
        "synapscale.com" in db_host.lower(),
        db_host.startswith("do-user-"),  # DigitalOcean
    ])
    
    if is_production:
        print(f"\n{Colors.RED}{Colors.BOLD}🚨 AMBIENTE DE PRODUÇÃO DETECTADO! 🚨{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}   RISCO EXTREMO - PODE QUEBRAR O SISTEMA{Colors.END}")
    
    return is_production

def get_user_confirmations():
    """Solicita confirmações múltiplas do usuário"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}CONFIRMAÇÕES OBRIGATÓRIAS:{Colors.END}")
    
    # Primeira confirmação
    resp1 = input(f"\n{Colors.WHITE}1. Você fez BACKUP do banco antes? (digite 'SIM-FIZ-BACKUP'): {Colors.END}")
    if resp1 != "SIM-FIZ-BACKUP":
        print(f"{Colors.RED}❌ Operação cancelada. Faça backup primeiro!{Colors.END}")
        return False
    
    # Segunda confirmação
    resp2 = input(f"\n{Colors.WHITE}2. Você entende que este script BYPASSA a API? (digite 'ENTENDO-OS-RISCOS'): {Colors.END}")
    if resp2 != "ENTENDO-OS-RISCOS":
        print(f"{Colors.RED}❌ Operação cancelada. Você deve entender os riscos!{Colors.END}")
        return False
    
    # Terceira confirmação
    resp3 = input(f"\n{Colors.WHITE}3. Confirma que quer MODIFICAR o banco diretamente? (digite 'MODIFICAR-BANCO-DIRETO'): {Colors.END}")
    if resp3 != "MODIFICAR-BANCO-DIRETO":
        print(f"{Colors.RED}❌ Operação cancelada por segurança!{Colors.END}")
        return False
    
    return True

def create_saas_user_direct():
    """Criar usuário SaaS diretamente na estrutura correta - PERIGOSO!"""
    
    # Mostrar avisos de perigo
    show_danger_warning()
    
    # Detectar ambiente
    is_production = get_environment_info()
    
    # Confirmação extra para produção
    if is_production:
        print(f"\n{Colors.RED}{Colors.BOLD}🚨 ÚLTIMA CHANCE - AMBIENTE DE PRODUÇÃO 🚨{Colors.END}")
        final_confirm = input(f"{Colors.RED}Digite 'EXECUTAR-EM-PRODUCAO-COM-RISCO' para continuar: {Colors.END}")
        if final_confirm != "EXECUTAR-EM-PRODUCAO-COM-RISCO":
            print(f"{Colors.GREEN}✅ Operação cancelada por segurança. Decisão sábia!{Colors.END}")
            return None
    
    # Obter confirmações do usuário
    if not get_user_confirmations():
        return None
    
    print(f"\n{Colors.RED}{Colors.BOLD}🔄 Executando operação PERIGOSA no banco...{Colors.END}")

    # Dados do usuário (DEVE VIR DO .env em produção)
    user_data = {
        "email": os.getenv("ADMIN_EMAIL", "admin@synapscale.com"),
        "username": "admin",
        "full_name": "Administrador SynapScale",
        "password": os.getenv("ADMIN_PASSWORD", "SynapScale2024!"),
    }
    
    print(f"\n{Colors.YELLOW}⚠️  Dados do usuário:{Colors.END}")
    print(f"   Email: {user_data['email']}")
    print(f"   Username: {user_data['username']}")
    print(f"   Nome: {user_data['full_name']}")
    print(f"   Senha: {'[CONFIGURADA NO .env]' if os.getenv('ADMIN_PASSWORD') else '[HARDCODED - PERIGOSO]'}")

    # Credenciais do banco
    config = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "sslmode": os.getenv("DB_SSLMODE", "require"),
    }
    try:
        # Conectar ao banco
        print(f"\n{Colors.RED}🔌 CONECTANDO DIRETAMENTE AO BANCO...{Colors.END}")
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()

        print(f"{Colors.GREEN}✅ Conectado ao banco (CONEXÃO DIRETA ATIVA){Colors.END}")

        # Gerar hash da senha
        print(f"{Colors.YELLOW}🔐 Gerando hash da senha...{Colors.END}")
        password_bytes = user_data["password"].encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

        # Gerar UUID para o usuário
        user_id = str(uuid.uuid4())

        # Verificar se usuário já existe
        print(f"{Colors.CYAN}🔍 Verificando se usuário já existe...{Colors.END}")
        cursor.execute(
            "SELECT id FROM synapscale_db.users WHERE email = %s OR username = %s",
            (user_data["email"], user_data["username"]),
        )
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"{Colors.YELLOW}⚠️  Usuário já existe com ID: {existing_user[0]}{Colors.END}")
            print(f"{Colors.YELLOW}   Operação não executada (usuário já criado){Colors.END}")
            cursor.close()
            conn.close()
            return existing_user[0]

        # ÚLTIMA CONFIRMAÇÃO antes de inserir
        print(f"\n{Colors.RED}{Colors.BOLD}🚨 ÚLTIMA CONFIRMAÇÃO ANTES DE MODIFICAR O BANCO 🚨{Colors.END}")
        print(f"{Colors.RED}   Esta operação VAI INSERIR dados diretamente no PostgreSQL{Colors.END}")
        print(f"{Colors.RED}   SEM passar por validações da aplicação{Colors.END}")
        
        final_final = input(f"\n{Colors.RED}Digite 'INSERIR-DADOS-DIRETO-NO-BANCO' para confirmar: {Colors.END}")
        if final_final != "INSERIR-DADOS-DIRETO-NO-BANCO":
            print(f"{Colors.GREEN}✅ Operação cancelada na última hora. Boa decisão!{Colors.END}")
            cursor.close()
            conn.close()
            return None

        # Inserir usuário na tabela correta
        print(f"\n{Colors.RED}{Colors.BOLD}💀 EXECUTANDO INSERT DIRETO NO BANCO...{Colors.END}")
        insert_query = """
            INSERT INTO synapscale_db.users 
            (id, email, username, full_name, hashed_password, is_active, is_superuser, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """

        now = datetime.utcnow()
        cursor.execute(
            insert_query,
            (
                user_id,
                user_data["email"],
                user_data["username"],
                user_data["full_name"],
                hashed_password,
                True,  # is_active
                True,  # is_superuser
                now,  # created_at
                now,  # updated_at
            ),
        )

        inserted_id = cursor.fetchone()[0]

        # Confirmar transação
        print(f"{Colors.RED}💾 COMMITANDO TRANSAÇÃO (modificação permanente)...{Colors.END}")
        conn.commit()

        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ USUÁRIO CRIADO DIRETAMENTE NO BANCO!{Colors.END}")
        print(f"{Colors.WHITE}📧 Email: {Colors.CYAN}{user_data['email']}{Colors.END}")
        print(f"{Colors.WHITE}👤 Username: {Colors.CYAN}{user_data['username']}{Colors.END}")
        print(f"{Colors.WHITE}🆔 ID: {Colors.CYAN}{inserted_id}{Colors.END}")
        print(f"{Colors.WHITE}🔐 Senha: {Colors.CYAN}{user_data['password']}{Colors.END}")
        print(f"{Colors.WHITE}👑 Tipo: {Colors.RED}SUPERUSER (administrador){Colors.END}")

        # Verificar se foi realmente criado
        cursor.execute("SELECT COUNT(*) FROM synapscale_db.users;")
        total_users = cursor.fetchone()[0]
        print(f"\n{Colors.YELLOW}📊 Total de usuários na base: {total_users}{Colors.END}")

        print(f"\n{Colors.MAGENTA}{Colors.BOLD}⚠️  LEMBRE-SE:{Colors.END}")
        print(f"{Colors.MAGENTA}   - Este usuário foi criado SEM validações{Colors.END}")
        print(f"{Colors.MAGENTA}   - Pode haver inconsistências com a aplicação{Colors.END}")
        print(f"{Colors.MAGENTA}   - Monitore logs da aplicação para problemas{Colors.END}")
        print(f"{Colors.MAGENTA}   - Considere recriar via API quando possível{Colors.END}")

        cursor.close()
        conn.close()

        return inserted_id

    except Exception as e:
        print(f"\n{Colors.RED}❌ ERRO ao executar operação perigosa: {str(e)}{Colors.END}")
        print(f"{Colors.RED}   A operação direta no banco falhou{Colors.END}")
        if "conn" in locals():
            print(f"{Colors.YELLOW}🔄 Fazendo rollback da transação...{Colors.END}")
            conn.rollback()
        return None


if __name__ == "__main__":
    print(f"{Colors.RED}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}🚨 SCRIPT DE MANIPULAÇÃO DIRETA DO BANCO DE DADOS 🚨{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}{'='*80}{Colors.END}")
    
    print(f"\n{Colors.WHITE}{Colors.BOLD}Este script é para EMERGÊNCIAS apenas!{Colors.END}")
    print(f"{Colors.WHITE}Use create_saas_user.py (via API) em situações normais.{Colors.END}")
    
    # Verificar se variáveis críticas estão configuradas
    critical_vars = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing_vars = [var for var in critical_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\n{Colors.RED}❌ ERRO: Variáveis críticas não configuradas no .env:{Colors.END}")
        for var in missing_vars:
            print(f"{Colors.RED}   - {var}{Colors.END}")
        print(f"\n{Colors.YELLOW}Configure todas as variáveis no .env antes de continuar.{Colors.END}")
        sys.exit(1)
    
    user_id = create_saas_user_direct()
    
    if user_id:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 OPERAÇÃO PERIGOSA CONCLUÍDA!{Colors.END}")
        print(f"{Colors.GREEN}   Usuário criado diretamente no banco de dados{Colors.END}")
        print(f"{Colors.WHITE}   ID do usuário: {Colors.CYAN}{user_id}{Colors.END}")
        
        print(f"\n{Colors.YELLOW}{Colors.BOLD}📋 PRÓXIMOS PASSOS:{Colors.END}")
        print(f"{Colors.WHITE}1. Teste o login via API{Colors.END}")
        print(f"{Colors.WHITE}2. Monitore logs da aplicação{Colors.END}")
        print(f"{Colors.WHITE}3. Verifique se há inconsistências{Colors.END}")
        print(f"{Colors.WHITE}4. Considere migrar para criação via API{Colors.END}")
        
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}⚠️  ATENÇÃO CONTÍNUA:{Colors.END}")
        print(f"{Colors.MAGENTA}   Este usuário bypassa validações da aplicação{Colors.END}")
        print(f"{Colors.MAGENTA}   Pode ter comportamento inesperado no sistema{Colors.END}")
        
    elif user_id is None:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ OPERAÇÃO CANCELADA COM SEGURANÇA{Colors.END}")
        print(f"{Colors.GREEN}   Nenhuma modificação foi feita no banco{Colors.END}")
        print(f"{Colors.WHITE}   Considere usar create_saas_user.py (via API){Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ FALHA NA OPERAÇÃO PERIGOSA{Colors.END}")
        print(f"{Colors.RED}   Erro ao criar usuário diretamente no banco{Colors.END}")
        print(f"{Colors.WHITE}   Verifique logs acima para detalhes do erro{Colors.END}")
        print(f"{Colors.WHITE}   Considere usar create_saas_user.py (via API){Colors.END}")
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}💡 LEMBRETE:{Colors.END}")
    print(f"{Colors.CYAN}   Para operações normais, sempre prefira:{Colors.END}")
    print(f"{Colors.CYAN}   python tools/database/create_saas_user.py{Colors.END}")
    
    print(f"\n{Colors.WHITE}{'='*80}{Colors.END}")
