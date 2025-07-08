#!/usr/bin/env python3
import sys
import json
import re
from collections import OrderedDict

DUPLICATE_PATH_RE = re.compile(r"/([a-zA-Z0-9_]+)/\1(/|$)")

def fix_path_value(val):
    if not isinstance(val, str):
        return val
    while True:
        new_val = DUPLICATE_PATH_RE.sub(r"/\1\2", val)
        if new_val == val:
            break
        val = new_val
    return val

def fix_paths_in_obj(obj):
    if isinstance(obj, dict):
        new_obj = OrderedDict()
        for k, v in obj.items():
            if k == 'path' or k.endswith('_path') or k.endswith('Path'):
                new_obj[k] = fix_path_value(v)
            else:
                new_obj[k] = fix_paths_in_obj(v)
        return new_obj
    elif isinstance(obj, list):
        return [fix_paths_in_obj(i) for i in obj]
    else:
        return obj

def main():
    if len(sys.argv) < 2:
        print("Uso: fix_duplicate_paths_json_values.py <arquivo.json>")
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)
    fixed = fix_paths_in_obj(data)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(fixed, f, ensure_ascii=False, indent=2)
    print(f"Valores de path corrigidos em {path}")

if __name__ == "__main__":
    main() 