#!/usr/bin/env python
"""
Script para executar o SynapScale Backend com o Memory Bank habilitado
"""
import os
import sys
import logging
import subprocess
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("synapse-memory-bank-runner")

def main():
    """
    Função principal para executar o SynapScale Backend com o Memory Bank
    """
    try:
        # Verificar se o Memory Bank está instalado
        try:
            import memory_bank
            logger.info("Memory Bank está instalado")
        except ImportError:
            logger.error("Memory Bank não está instalado. Execute ./install_memory_bank.sh primeiro.")
            return False
        
        # Configurar variáveis de ambiente
        os.environ["ENABLE_MEMORY_BANK"] = "true"
        
        # Verificar qual script de inicialização usar
        dev_script = Path("./dev.sh")
        prod_script = Path("./prod.sh")
        
        if dev_script.exists() and os.access(dev_script, os.X_OK):
            script = "./dev.sh"
            logger.info("Executando SynapScale Backend em modo de desenvolvimento com Memory Bank habilitado")
        elif prod_script.exists() and os.access(prod_script, os.X_OK):
            script = "./prod.sh"
            logger.info("Executando SynapScale Backend em modo de produção com Memory Bank habilitado")
        else:
            logger.error("Nenhum script de inicialização encontrado (dev.sh ou prod.sh)")
            return False
        
        # Executar o script
        process = subprocess.Popen(script, shell=True)
        
        # Aguardar o processo terminar
        process.wait()
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Operação cancelada pelo usuário")
        return False
    except Exception as e:
        logger.error(f"Erro ao executar SynapScale Backend: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro não tratado: {e}")
        sys.exit(1)
