#!/usr/bin/env python3
import sys
import json
import re
from collections import OrderedDict

# Regex para detectar duplicação de segmento
DUPLICATE_PATH_RE = re.compile(r"/([a-zA-Z0-9_]+)/\1(/|$)")

def fix_key(key):
    # Corrige todas as duplicações do tipo /segment/segment/ para /segment/
    while True:
        new_key = DUPLICATE_PATH_RE.sub(r"/\1\2", key)
        if new_key == key:
            break
        key = new_key
    return key

def fix_dict_keys(obj):
    if isinstance(obj, dict):
        new_obj = OrderedDict()
        for k, v in obj.items():
            new_k = fix_key(k) if isinstance(k, str) else k
            new_obj[new_k] = fix_dict_keys(v)
        return new_obj
    elif isinstance(obj, list):
        return [fix_dict_keys(i) for i in obj]
    else:
        return obj

def main():
    if len(sys.argv) < 2:
        print("Uso: fix_duplicate_paths_json_keys.py <arquivo.json>")
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)
    fixed = fix_dict_keys(data)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(fixed, f, ensure_ascii=False, indent=2)
    print(f"Chaves duplicadas corrigidas em {path}")

if __name__ == "__main__":
    main() 