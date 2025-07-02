#!/bin/bash

# 🧹 Script: Servidor com Logs Limpos e Organizados
# 
# Este script inicia o servidor e filtra automaticamente 
# os logs para mostrar apenas informações relevantes
# de autenticação, sem spam desnecessário.

echo "🧹 INICIANDO SERVIDOR COM LOGS ORGANIZADOS"
echo "==========================================="
echo ""
echo "🔥 Filtros ativos:"
echo "   ✅ Logs de LOGIN (SUCCESS/FAILED)" 
echo "   ✅ Logs de AUTH endpoints"
echo "   ✅ Logs de ERROR/WARNING"
echo "   ❌ Spam de current-url, identity, health"
echo ""
echo "🎯 Para testar, execute em outro terminal:"
echo "   python test_auth_logs.py"
echo ""
echo "==========================================="
echo ""

# Ativar ambiente virtual se não estiver ativo
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "🔄 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Parar qualquer servidor rodando
echo "🛑 Parando servidores existentes..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "uvicorn.*main" 2>/dev/null || true
sleep 2

echo "🚀 Iniciando servidor com logs filtrados..."
echo ""

# Iniciar servidor com filtro de logs
python src/synapse/main.py 2>&1 | grep -E --line-buffered '🔐|/auth/|ERROR|WARNING|CRITICAL|Exception|INFO.*auth|server.*start|Application.*ready' | while read line; do
    # Adicionar timestamp mais visível para logs importantes
    timestamp=$(date '+%H:%M:%S')
    
    # Colorir logs conforme o tipo
    if [[ "$line" =~ "🔐 ✅ LOGIN SUCCESS" ]]; then
        echo -e "\033[92m[$timestamp] 🎉 $line\033[0m"  # Verde brilhante
    elif [[ "$line" =~ "🔐 ❌ LOGIN FAILED" ]]; then
        echo -e "\033[91m[$timestamp] ⚠️  $line\033[0m"  # Vermelho
    elif [[ "$line" =~ "🔐" ]]; then
        echo -e "\033[94m[$timestamp] 🔐 $line\033[0m"  # Azul
    elif [[ "$line" =~ "/auth/" ]]; then
        echo -e "\033[93m[$timestamp] 🔑 $line\033[0m"  # Amarelo
    elif [[ "$line" =~ "ERROR|CRITICAL|Exception" ]]; then
        echo -e "\033[91m[$timestamp] ❌ $line\033[0m"  # Vermelho
    elif [[ "$line" =~ "WARNING" ]]; then
        echo -e "\033[93m[$timestamp] ⚠️  $line\033[0m"  # Amarelo
    else
        echo "[$timestamp] $line"
    fi
done 