import os
import re

# Mapeamento de duplicações para caminhos corretos
DUPLICATE_PATHS = {
    "/features/": "/features/",
    "/migration/": "/migration/",
    "/rbac/": "/rbac/",
    "/payments/": "/payments/",
    "/templates/": "/templates/",
    "/marketplace/": "/marketplace/",
    "/analytics/": "/analytics/",
    "/workflows/": "/workflows/",
    "/agents/": "/agents/",
    # Adicione outros padrões conforme necessário
}

# Extensões de arquivos a serem processados
INCLUDE_EXTENSIONS = (".py", ".js", ".ts", ".json", ".yaml", ".yml", ".md")


def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    original_content = content
    for wrong, right in replacements.items():
        # Substituição só se for path completo (evita falso positivo)
        content = re.sub(re.escape(wrong), right, content)
    if content != original_content:
        # Backup antes de sobrescrever
        os.rename(filepath, filepath + ".bak")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Corrigido: {filepath}")

def walk_and_replace(root_dir, replacements):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(INCLUDE_EXTENSIONS):
                filepath = os.path.join(dirpath, filename)
                replace_in_file(filepath, replacements)

if __name__ == "__main__":
    # Caminho do repositório raiz
    REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
    walk_and_replace(REPO_ROOT, DUPLICATE_PATHS)
    print("Correção de endpoints duplicados concluída.")
