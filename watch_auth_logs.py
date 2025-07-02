#!/usr/bin/env python3
"""
📺 Monitor de Logs de Autenticação - Tempo Real

Este script monitora e filtra logs de autenticação em tempo real,
mostrando apenas as informações relevantes de forma organizada.
"""

import subprocess
import sys
import re
import time
from datetime import datetime

def print_banner():
    """Exibe banner inicial"""
    print("\n" + "=" * 60)
    print("📺 MONITOR DE LOGS DE AUTENTICAÇÃO - TEMPO REAL")
    print("=" * 60)
    print("🔥 Mostrando apenas logs relevantes (sem spam)")
    print("🔐 Filtros: LOGIN SUCCESS/FAILED + outros endpoints AUTH")
    print("📊 Excluídos: current-url, identity, health, metrics")
    print("=" * 60)
    print("💡 Execute testes em outro terminal para ver os logs")
    print("🧪 Comando: python test_auth_logs.py")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🔍 AGUARDANDO LOGS...")

def filter_log_line(line):
    """
    Filtra e formata linhas de log relevantes.
    
    Retorna:
        tuple: (should_display, formatted_line)
    """
    line = line.strip()
    
    if not line:
        return False, ""
    
    # Filtros de logs irrelevantes (EXCLUIR)
    excluded_patterns = [
        r"current-url",
        r"\.identity", 
        r"/health",
        r"/metrics",
        r"/favicon\.ico",
        r"GET.*docs",
        r"GET.*static",
        r"watchfiles",
        r"INFO.*uvicorn",
        r"Started server process",
        r"Waiting for application startup",
        r"Application startup complete"
    ]
    
    for pattern in excluded_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return False, ""
    
    # Destacar logs de autenticação ESPECIAIS
    if "🔐" in line:
        # Log já formatado - apenas destacar mais
        if "✅ LOGIN SUCCESS" in line:
            formatted = f"🎉 {line}"
            return True, f"\033[92m{formatted}\033[0m"  # Verde
        elif "❌ LOGIN FAILED" in line:
            formatted = f"⚠️  {line}"
            return True, f"\033[91m{formatted}\033[0m"  # Vermelho
        else:
            return True, f"\033[94m{line}\033[0m"  # Azul
    
    # Logs de endpoints AUTH em geral
    if "/auth/" in line:
        return True, f"\033[93m🔑 {line}\033[0m"  # Amarelo
    
    # Logs de erro (importantes)
    if any(level in line for level in ["ERROR", "CRITICAL", "Exception"]):
        return True, f"\033[91m❌ {line}\033[0m"  # Vermelho
    
    # Logs de warning (importantes)
    if "WARNING" in line:
        return True, f"\033[93m⚠️  {line}\033[0m"  # Amarelo
    
    # Outros logs importantes (startup, connections, etc.)
    important_patterns = [
        r"server.*start",
        r"database.*connect",
        r"application.*ready",
        r"POST.*api.*v1",
        r"PUT.*api.*v1", 
        r"DELETE.*api.*v1"
    ]
    
    for pattern in important_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return True, f"📡 {line}"
    
    # Por padrão, não mostrar outros logs
    return False, ""

def monitor_logs():
    """Monitora logs em tempo real"""
    print_banner()
    
    try:
        # Iniciar processo para seguir logs do servidor
        # Assumindo que o servidor está rodando com stdout/stderr visível
        cmd = ["python", "-u", "src/synapse/main.py"]
        
        # Tentar conectar a um processo já rodando via tail/grep
        try:
            # Método alternativo: usar journalctl, logs do sistema, ou tail de arquivo
            # Por enquanto, vamos simular o monitoring
            
            print("🔄 Tentando conectar aos logs do servidor...")
            print("📌 Execute 'python test_auth_logs.py' em outro terminal")
            print("\n" + "-" * 60)
            
            # Loop de monitoramento simulado
            # Em produção, isto seria conectado aos logs reais
            count = 0
            while True:
                time.sleep(1)
                count += 1
                
                if count % 10 == 0:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"⏳ {timestamp} - Aguardando atividade de login...")
                
                # Aqui você conectaria aos logs reais do servidor
                # Por exemplo: seguindo um arquivo de log ou stdout do processo
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoramento interrompido pelo usuário")
            
    except Exception as e:
        print(f"\n❌ Erro ao monitorar logs: {e}")
        print("\n💡 Dicas para resolver:")
        print("   1. Verifique se o servidor está rodando")
        print("   2. Execute: python src/synapse/main.py")
        print("   3. Em outro terminal: python test_auth_logs.py")

def show_manual_instructions():
    """Mostra instruções manuais para visualizar logs"""
    print("\n" + "=" * 60)
    print("📋 INSTRUÇÕES MANUAIS - LOGS ORGANIZADOS")
    print("=" * 60)
    
    print("\n🎯 MÉTODO 1: Logs do Servidor Direto")
    print("-" * 30)
    print("Terminal 1 (Servidor):")
    print("   python src/synapse/main.py")
    print("\nTerminal 2 (Testes):")
    print("   python test_auth_logs.py")
    print("\n✅ Resultado: Logs aparecerão no Terminal 1")
    
    print("\n🎯 MÉTODO 2: Filtro em Tempo Real")
    print("-" * 30)
    print("Terminal 1 (Servidor com filtro):")
    print("   python src/synapse/main.py 2>&1 | grep -E '🔐|AUTH|ERROR|WARNING'")
    print("\nTerminal 2 (Testes):")
    print("   python test_auth_logs.py")
    
    print("\n🎯 FORMATO DOS NOVOS LOGS:")
    print("-" * 30)
    print("✅ LOGIN SUCCESS:")
    print("   🔐 ✅ LOGIN SUCCESS | User: user@email.com | Input: user@email.com | Method: EMAIL | IP: 127.0.0.1")
    print("\n❌ LOGIN FAILED:")
    print("   🔐 ❌ LOGIN FAILED | Input: user@email.com | Reason: WRONG_PASSWORD | IP: 127.0.0.1")
    print("\n🔑 AUTH REQUEST:")
    print("   🔐 AUTH | POST /api/v1/auth/login - 200 - 0.123s - 127.0.0.1")
    
    print("\n🚫 LOGS FILTRADOS (não aparecem mais):")
    print("-" * 30)
    print("   ❌ POST /current-url")
    print("   ❌ GET /.identity")
    print("   ❌ GET /health")
    print("   ❌ GET /metrics")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_manual_instructions()
    else:
        show_manual_instructions()
        print("\n⚡ Para monitoramento automático (em desenvolvimento):")
        print("   python watch_auth_logs.py --monitor") 