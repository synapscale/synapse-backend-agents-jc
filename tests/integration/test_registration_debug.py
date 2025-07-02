"""
Debug script para identificar problemas no registro de usuário
Foco no problema do plan_id sendo None durante criação de workspace
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": f"debug_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com",
    "username": f"debug_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "full_name": "Debug User Test",
    "password": "TestPassword123!@#",
}


def test_server_status():
    """Verifica se o servidor está rodando"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Servidor está rodando - Status: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Servidor não está rodando: {e}")
        return False


def test_database_connection():
    """Testa conexão com banco de dados via endpoint health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False


def test_registration():
    """Testa o registro de usuário com logs detalhados"""
    print(f"\n🔍 Testando registro do usuário:")
    print(f"   Email: {TEST_USER['email']}")
    print(f"   Username: {TEST_USER['username']}")

    try:
        # Fazer requisição de registro
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=TEST_USER,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        print(f"\n📡 Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")

        if response.status_code == 201:
            data = response.json()
            print(f"✅ Usuário registrado com sucesso!")
            print(f"   ID: {data.get('id')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Nome: {data.get('full_name')}")
            return True, data

        elif response.status_code == 400:
            error_data = response.json()
            print(f"❌ Erro de validação: {error_data}")
            return False, error_data

        elif response.status_code == 500:
            print(f"❌ Erro interno do servidor (500)")
            try:
                error_data = response.json()
                print(f"   Detalhes: {error_data}")
            except:
                print(f"   Response text: {response.text}")
            return False, {"error": "Internal server error", "status": 500}

        else:
            print(f"❌ Status inesperado: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, {"error": f"Unexpected status {response.status_code}"}

    except requests.exceptions.Timeout:
        print(f"❌ Timeout na requisição (30s)")
        return False, {"error": "Request timeout"}

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False, {"error": str(e)}


def test_login(email, password):
    """Testa login do usuário registrado"""
    print(f"\n🔐 Testando login do usuário:")

    try:
        # Dados do form para login
        form_data = {
            "username": email,  # OAuth2PasswordRequestForm usa 'username' para email
            "password": password,
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=form_data,  # usar data em vez de json para form
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )

        print(f"📡 Login Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login realizado com sucesso!")
            print(f"   Token Type: {data.get('token_type')}")
            print(f"   Expires In: {data.get('expires_in')}s")
            return True, data.get("access_token")
        else:
            print(f"❌ Falha no login: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False, None

    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False, None


def test_user_info(token):
    """Testa endpoint /me para ver informações do usuário"""
    print(f"\n👤 Testando informações do usuário:")

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=10
        )

        print(f"📡 User Info Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Informações do usuário obtidas!")
            print(f"   ID: {data.get('id')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Nome: {data.get('full_name')}")
            print(f"   Verificado: {data.get('is_verified')}")
            print(f"   Ativo: {data.get('is_active')}")
            return True, data
        else:
            print(f"❌ Falha ao obter informações: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None

    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")
        return False, None


def test_workspaces(token):
    """Testa listagem de workspaces para ver se foi criado o workspace padrão"""
    print(f"\n🏢 Testando workspaces do usuário:")

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            f"{BASE_URL}/api/v1/workspaces/", headers=headers, timeout=10
        )

        print(f"📡 Workspaces Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Workspaces obtidos!")

            if "items" in data:
                workspaces = data["items"]
                print(f"   Total de workspaces: {len(workspaces)}")

                for workspace in workspaces:
                    print(f"   - ID: {workspace.get('id')}")
                    print(f"     Nome: {workspace.get('name')}")
                    print(f"     Tipo: {workspace.get('type')}")
                    print(f"     Plan ID: {workspace.get('plan_id')}")
                    print(f"     Owner ID: {workspace.get('owner_id')}")
            else:
                print(f"   Response: {data}")

            return True, data
        else:
            print(f"❌ Falha ao obter workspaces: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None

    except Exception as e:
        print(f"❌ Erro ao obter workspaces: {e}")
        return False, None


def main():
    """Função principal de teste"""
    print("=" * 60)
    print("🐛 DEBUG: Teste de Registro e Workspace Creation")
    print("=" * 60)

    # 1. Verificar servidor
    if not test_server_status():
        print("\n❌ Abortando: servidor não está rodando")
        sys.exit(1)

    # 2. Verificar banco de dados
    if not test_database_connection():
        print("\n⚠️  Aviso: health check falhou, mas continuando...")

    # 3. Testar registro
    registration_success, registration_data = test_registration()

    if not registration_success:
        print(f"\n❌ Registro falhou. Detalhes:")
        print(json.dumps(registration_data, indent=2))

        # Se o erro for de plan_id None, mostrar informações específicas
        if "plan_id" in str(registration_data).lower():
            print(f"\n🎯 PROBLEMA IDENTIFICADO: plan_id está None!")
            print(f"   Isso indica que o plano FREE não foi criado ou encontrado")
            print(f"   Verifique:")
            print(f"   1. Se a migração de planos foi executada")
            print(f"   2. Se existe plano com slug 'free' no banco")
            print(f"   3. Se o modelo Plan está funcionando corretamente")

        return

    # 4. Testar login
    login_success, access_token = test_login(TEST_USER["email"], TEST_USER["password"])

    if not login_success:
        print(
            f"\n❌ Login falhou, mas registro funcionou. Possível problema de autenticação."
        )
        return

    # 5. Testar informações do usuário
    user_info_success, user_data = test_user_info(access_token)

    # 6. Testar workspaces
    workspaces_success, workspaces_data = test_workspaces(access_token)

    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"✅ Servidor rodando: SIM")
    print(
        f"{'✅' if registration_success else '❌'} Registro de usuário: {'SIM' if registration_success else 'NÃO'}"
    )
    print(
        f"{'✅' if login_success else '❌'} Login: {'SIM' if login_success else 'NÃO'}"
    )
    print(
        f"{'✅' if user_info_success else '❌'} Informações do usuário: {'SIM' if user_info_success else 'NÃO'}"
    )
    print(
        f"{'✅' if workspaces_success else '❌'} Workspaces: {'SIM' if workspaces_success else 'NÃO'}"
    )

    if (
        registration_success
        and login_success
        and user_info_success
        and workspaces_success
    ):
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        print(f"   O problema do plan_id parece ter sido resolvido.")
    else:
        print(f"\n⚠️  ALGUNS TESTES FALHARAM")
        print(f"   Verifique os logs acima para detalhes específicos.")


if __name__ == "__main__":
    main()
