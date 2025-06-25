#!/usr/bin/env python
"""
Script para executar as migrações do Memory Bank
"""
import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("memory-bank-migrations")

def main():
    """
    Função principal para executar as migrações
    """
    try:
        # Importar o script de criação de tabelas
        from memory_bank.migrations.create_memory_bank_tables import run_migrations
        
        # Executar as migrações
        logger.info("Executando migrações do Memory Bank...")
        success = run_migrations()
        
        if success:
            logger.info("Migrações do Memory Bank executadas com sucesso!")
        else:
            logger.error("Falha ao executar migrações do Memory Bank")
            return False
        
        return True
        
    except ImportError as e:
        logger.error(f"Erro ao importar módulo de migrações: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro ao executar migrações: {e}")
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
