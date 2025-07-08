#!/usr/bin/env python3
"""
scripts/check_schema_alignment.py

Verifica o alinhamento entre a estrutura atual do banco de dados
(fonte da verdade) e os schemas definidos no OpenAPI (openapi.json).
Utiliza as variáveis do .env para conectar ao banco.
"""
import os
import sys
import json
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect


def load_env(env_path=".env"):
    """Carrega variáveis de ambiente do arquivo .env"""
    if not os.path.isfile(env_path):
        print(f"Erro: não encontrou {env_path}")
        sys.exit(1)
    load_dotenv(env_path, override=False)


def get_db_tables(schema):
    """Retorna lista de tabelas no schema especificado"""
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL não definido no .env")
        sys.exit(1)
    engine = create_engine(url)
    insp = inspect(engine)
    return insp.get_table_names(schema=schema), insp


def load_openapi(path="openapi.json"):
    """Carrega o spec OpenAPI JSON"""
    if not os.path.isfile(path):
        print(f"Erro: não encontrou {path}")
        print("Execute 'python -c \"import sys; sys.path.insert(0, 'src'); from synapse.main import app; import json; spec=app.openapi(); json.dump(spec, open('openapi.json', 'w'), indent=2)\"'")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_alignment(schema_name, tables, insp, spec):
    """Compara tabelas do DB com paths e componentes do spec"""
    mismatches = []
    components = spec.get("components", {}).get("schemas", {})
    paths = spec.get("paths", {})
    skip_cols = {"id", "created_at", "updated_at", "deleted_at"}

    for path, methods in paths.items():
        m = re.match(r"^/api/v1/([^/{]+)", path)
        if not m:
            continue
        table = m.group(1)
        if table not in tables:
            continue
        # obter colunas reais
        cols = [c["name"] for c in insp.get_columns(table, schema=schema_name)]
        colset = set(cols)
        for verb, op in methods.items():
            verb = verb.lower()
            if verb not in ("get", "post", "put", "patch"):
                continue
            # request body
            if verb in ("post", "put", "patch"):
                req = op.get("requestBody", {}).get("content", {})
                for media in req.values():
                    sch = media.get("schema", {})
                    if "$ref" in sch:
                        ref = sch["$ref"].split("/")[-1]
                        props = set(
                            components.get(ref, {}).get("properties", {}).keys()
                        )
                        missing = sorted(props - colset)
                        extra = sorted(colset - props - skip_cols)
                        if missing or extra:
                            mismatches.append(
                                (table, verb, "request", ref, missing, extra)
                            )
            # response body
            resp = op.get("responses", {}).get("200", {}).get("content", {})
            for media in resp.values():
                sch = media.get("schema", {})
                ref = None
                if "$ref" in sch:
                    ref = sch["$ref"].split("/")[-1]
                elif isinstance(sch.get("items"), dict) and "$ref" in sch["items"]:
                    ref = sch["items"]["$ref"].split("/")[-1]
                if ref:
                    props = set(components.get(ref, {}).get("properties", {}).keys())
                    missing = sorted(props - colset)
                    extra = sorted(colset - props - skip_cols)
                    if missing or extra:
                        mismatches.append(
                            (table, verb, "response", ref, missing, extra)
                        )
    return mismatches


def main():
    load_env()
    schema = os.getenv("DATABASE_SCHEMA")
    if not schema:
        print("DATABASE_SCHEMA não definido no .env")
        sys.exit(1)
    tables, insp = get_db_tables(schema)
    spec = load_openapi()
    mismatches = analyze_alignment(schema, tables, insp, spec)
    if not mismatches:
        print("✔️ Nenhuma inconsistência encontrada entre DB e OpenAPI")
        return
    print(f"⚠️ {len(mismatches)} inconsistências encontradas:")
    for tpl in mismatches:
        table, verb, kind, ref, missing, extra = tpl
        print(f"  - [{table}][{verb}][{kind}] schema={ref}")
        if missing:
            print(f"      + Propriedades ausentes no DB: {missing}")
        if extra:
            print(f"      - Colunas extras no DB: {extra}")
    sys.exit(2)


if __name__ == "__main__":
    main()
