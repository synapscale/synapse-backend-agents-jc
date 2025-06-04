import os
import re

# Diretório base do projeto
BASE_DIR = "/workspaces/synapse-backend-agents-jc"

# Substituições a serem feitas
SUBSTITUTIONS = [
    # Substituir referências ao SQLite
    (r"sqlite:///.*?synapse\.db",
     "postgresql://user:password@localhost:5432/synapse"),
    (r"sqlite\+asyncpg:///.*?synapse\.db",
     "postgresql+asyncpg://user:password@localhost:5432/synapse"),
    (r"provider = \"sqlite\"", "provider = \"postgresql\""),

    # Remover dependências de SQLite
    (r"asyncpg", "asyncpg"),
]

# Extensões de arquivos a serem verificadas
ALLOWED_EXTENSIONS = [".py", ".prisma", ".env", ".ini", ".sh", ".md", ".json"]


def fix_references_in_file(file_path):
    """Corrige referências em um arquivo."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    original_content = content

    for pattern, replacement in SUBSTITUTIONS:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"✅ Corrigido: {file_path}")


def scan_and_fix(directory):
    """Percorre recursivamente o diretório e corrige os arquivos."""
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                file_path = os.path.join(root, file)
                fix_references_in_file(file_path)


if __name__ == "__main__":
    print("🚀 Iniciando correção de referências...")
    scan_and_fix(BASE_DIR)
    print("🎉 Correção concluída!")
