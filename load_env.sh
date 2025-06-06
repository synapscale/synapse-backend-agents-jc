#!/bin/bash
# Carregar variáveis de ambiente do arquivo .env
export $(grep -v '^#' .env | xargs)
