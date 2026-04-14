"""
Feishu Data Tool — Unified reader/writer for Feishu spreadsheets and bitables.

Subcommands:
    read          Read sheet or bitable content (markdown output)
    list-tables   List all tables in a bitable
    search        Search bitable records with filters
    create        Batch create records in a bitable table
    update        Update a single record by record_id
    delete        Batch delete records by record_ids

Auth: FEISHU_APP_ID + FEISHU_APP_SECRET env vars → tenant_access_token
"""

import argparse
import json
import os
import sys
import time
from urllib.parse import urlparse, parse_qs

try:
    import requests
except ImportError:
    print("Error: 'requests' library required. Install: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://open.feishu.cn/open-apis"


# ── Auth ─────────────────────────────────────────────────────────

def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Auth failed: {data.get('msg')} (code={data.get('code')})")
    return data["tenant_access_token"]


def get_auth():
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    if not app_id or not app_secret:
        print("Error: FEISHU_APP_ID and FEISHU_APP_SECRET env vars required.", file=sys.stderr)
        sys.exit(1)
    return get_tenant_access_token(app_id, app_secret)


# ── HTTP helpers ─────────────────────────────────────────────────

def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}


API_TIMEOUT = 30


def api_get(token: str, path: str, params: dict = None) -> dict:
    resp = requests.get(f"{BASE_URL}{path}", headers=_headers(token),
                        params=params or {}, timeout=API_TIMEOUT)
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"GET {path}: {data.get('msg')} (code={data.get('code')})")
    return data.get("data", {})


def api_post(token: str, path: str, body: dict) -> dict:
    resp = requests.post(f"{BASE_URL}{path}", headers=_headers(token),
                         json=body, timeout=API_TIMEOUT)
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"POST {path}: {data.get('msg')} (code={data.get('code')})")
    return data.get("data", {})


def api_put(token: str, path: str, body: dict) -> dict:
    resp = requests.put(f"{BASE_URL}{path}", headers=_headers(token),
                        json=body, timeout=API_TIMEOUT)
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"PUT {path}: {data.get('msg')} (code={data.get('code')})")
    return data.get("data", {})


# ── URL / Token Parsing ──────────────────────────────────────────

def parse_feishu_url(url: str) -> dict:
    parsed = urlparse(url)
    path = parsed.path
    query = parse_qs(parsed.query)

    if "/sheets/" in path:
        token = path.split("/sheets/")[-1].strip("/")
        return {"type": "sheet", "token": token}
    if "/wiki/" in path:
        token = path.split("/wiki/")[-1].strip("/")
        table_param = query.get("table", [None])[0]
        if table_param:
            return {"type": "bitable", "token": token, "table": table_param, "is_wiki": True}
        return {"type": "wiki_unknown", "token": token}
    if "/base/" in path:
        token = path.split("/base/")[-1].strip("/")
        table_param = query.get("table", [None])[0]
        return {"type": "bitable", "token": token, "table": table_param}
    return {"type": "unknown", "raw": url}


def resolve_wiki_to_actual(token: str, access_token: str) -> dict:
    data = api_get(access_token, "/wiki/v2/spaces/get_node", {"token": token})
    node = data.get("node", {})
    return {
        "obj_type": node.get("obj_type", ""),
        "obj_token": node.get("obj_token", ""),
        "title": node.get("title", ""),
    }


def resolve_bitable_token(url: str, access_token: str) -> tuple:
    """From a URL, resolve to (app_token, table_id). table_id may be None."""
    parsed = parse_feishu_url(url)
    table_id = None

    if parsed["type"] == "wiki_unknown":
        wiki = resolve_wiki_to_actual(parsed["token"], access_token)
        app_token = wiki["obj_token"]
        title = wiki.get("title", "")
        if title:
            print(f"Wiki node: {title} (type={wiki['obj_type']})", file=sys.stderr)
    elif parsed["type"] == "bitable":
        table_id = parsed.get("table")
        if parsed.get("is_wiki"):
            wiki = resolve_wiki_to_actual(parsed["token"], access_token)
            app_token = wiki["obj_token"]
        else:
            app_token = parsed["token"]
    elif parsed["type"] == "sheet":
        app_token = parsed["token"]
    else:
        raise ValueError(f"Cannot parse URL: {url}")

    return app_token, table_id


# ── Formatting helpers ───────────────────────────────────────────

def sanitize_cell(value) -> str:
    if value is None:
        return ""
    s = str(value).replace("|", "\\|").replace("\n", " ").replace("\r", "")
    if len(s) > 200:
        s = s[:197] + "..."
    return s


def extract_bitable_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                v = item.get("text") or item.get("name") or item.get("link") or ""
                if not v:
                    v = item.get("record_ids", item.get("table_id", ""))
                    if isinstance(v, list):
                        v = ",".join(str(x) for x in v if x)
                parts.append(str(v) if v else "")
            elif item is not None:
                parts.append(str(item))
        return ", ".join(p for p in parts if p)
    if isinstance(value, dict):
        for key in ("text", "name", "link"):
            v = value.get(key)
            if v is not None:
                return str(v)
        return json.dumps(value, ensure_ascii=False)
    return str(value)


# ── Subcommand: read ─────────────────────────────────────────────

def read_spreadsheet(spreadsheet_token: str, access_token: str) -> str:
    sheets_data = api_get(access_token, f"/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query")
    sheets = sheets_data.get("sheets", [])
    if not sheets:
        return "_No sheets found._\n"

    parts = []
    for sheet in sheets:
        sheet_id = sheet.get("sheet_id", "")
        title = sheet.get("title", sheet_id)

        try:
            values_data = api_get(
                access_token,
                f"/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}",
                {"valueRenderOption": "ToString"},
            )
            rows = values_data.get("valueRange", {}).get("values", [])
        except RuntimeError as e:
            parts.append(f"## Sheet: {title}\n\n_Error: {e}_\n")
            continue

        if not rows:
            parts.append(f"## Sheet: {title} (empty)\n")
            continue

        actual_cols = max(len(r) for r in rows)
        parts.append(f"## Sheet: {title} ({len(rows)} rows x {actual_cols} cols)\n")
        header = [sanitize_cell(c) for c in rows[0]]
        parts.append("| " + " | ".join(header) + " |")
        parts.append("| " + " | ".join(["---"] * len(header)) + " |")
        for row in rows[1:]:
            cells = [sanitize_cell(row[i] if i < len(row) else "") for i in range(len(header))]
            parts.append("| " + " | ".join(cells) + " |")
        parts.append("")
    return "\n".join(parts)


def read_bitable(app_token: str, access_token: str, table_id: str = None) -> str:
    tables_data = api_get(access_token, f"/bitable/v1/apps/{app_token}/tables")
    tables = tables_data.get("items", [])
    if not tables:
        return "_No tables found._\n"

    if table_id:
        tables = [t for t in tables if t.get("table_id") == table_id]
        if not tables:
            all_ids = [t.get("table_id") for t in tables_data.get("items", [])]
            return f"_Table '{table_id}' not found. Available: {all_ids}_\n"

    parts = []
    for table in tables:
        tid = table.get("table_id", "")
        tname = table.get("name", tid)

        fields_data = api_get(access_token, f"/bitable/v1/apps/{app_token}/tables/{tid}/fields")
        fields = fields_data.get("items", [])
        field_names = [f.get("field_name", f.get("field_id", "")) for f in fields]

        all_records = []
        page_token = None
        while True:
            params = {"page_size": 500}
            if page_token:
                params["page_token"] = page_token
                time.sleep(0.2)
            records_data = api_get(access_token, f"/bitable/v1/apps/{app_token}/tables/{tid}/records", params)
            all_records.extend(records_data.get("items", []))
            if not records_data.get("has_more"):
                break
            page_token = records_data.get("page_token")

        parts.append(f"## Table: {tname} ({len(all_records)} records x {len(field_names)} fields)")
        parts.append(f"table_id: `{tid}`\n")

        if not field_names:
            parts.append("_No fields._\n")
            continue

        parts.append("| record_id | " + " | ".join(field_names) + " |")
        parts.append("| --- | " + " | ".join(["---"] * len(field_names)) + " |")
        for record in all_records:
            rid = record.get("record_id", "")
            rf = record.get("fields", {})
            cells = [sanitize_cell(extract_bitable_value(rf.get(fn))) for fn in field_names]
            parts.append(f"| {rid} | " + " | ".join(cells) + " |")
        parts.append("")
    return "\n".join(parts)


def resolve_url(url: str, access_token: str) -> dict:
    """Unified URL resolution → {doc_type, app_token, table_id}."""
    parsed = parse_feishu_url(url)
    table_id = parsed.get("table")

    if parsed["type"] == "sheet":
        return {"doc_type": "sheet", "app_token": parsed["token"], "table_id": None}

    if parsed["type"] == "bitable":
        if parsed.get("is_wiki"):
            wiki = resolve_wiki_to_actual(parsed["token"], access_token)
            return {"doc_type": wiki.get("obj_type") or "bitable",
                    "app_token": wiki["obj_token"], "table_id": table_id,
                    "title": wiki.get("title", "")}
        return {"doc_type": "bitable", "app_token": parsed["token"], "table_id": table_id}

    if parsed["type"] == "wiki_unknown":
        wiki = resolve_wiki_to_actual(parsed["token"], access_token)
        return {"doc_type": wiki.get("obj_type") or "unknown",
                "app_token": wiki["obj_token"], "table_id": None,
                "title": wiki.get("title", "")}

    raise ValueError(f"Cannot parse URL: {url}")


def cmd_read(args):
    token = get_auth()
    info = resolve_url(args.url, token)
    table_id = args.table or info.get("table_id")

    if info.get("title"):
        print(f"Wiki node: {info['title']} (type={info['doc_type']})", file=sys.stderr)

    if info["doc_type"] == "sheet":
        result = read_spreadsheet(info["app_token"], token)
    else:
        result = read_bitable(info["app_token"], token, table_id)

    _output(result, args.output)


# ── Subcommand: list-tables ──────────────────────────────────────

def cmd_list_tables(args):
    token = get_auth()
    info = resolve_url(args.url, token)
    app_token = info["app_token"]

    tables_data = api_get(token, f"/bitable/v1/apps/{app_token}/tables")
    tables = tables_data.get("items", [])

    parts = [f"## Bitable Tables (app_token: `{app_token}`)\n"]
    parts.append("| table_id | name | revision |")
    parts.append("| --- | --- | --- |")
    for t in tables:
        parts.append(f"| {t.get('table_id','')} | {t.get('name','')} | {t.get('revision','')} |")
    parts.append("")

    _output("\n".join(parts), args.output)


# ── Subcommand: search ───────────────────────────────────────────

def cmd_search(args):
    token = get_auth()
    info = resolve_url(args.url, token)
    app_token = info["app_token"]
    table_id = args.table or info.get("table_id")
    if not table_id:
        print("Error: --table required for search.", file=sys.stderr)
        sys.exit(1)

    filter_obj = json.loads(args.filter) if args.filter else None
    body = {}
    if filter_obj:
        body["filter"] = filter_obj

    all_records = []
    page_token = None
    while True:
        params_str = f"?page_size=500"
        if page_token:
            params_str += f"&page_token={page_token}"
        path = f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/search{params_str}"
        data = api_post(token, path, body)
        all_records.extend(data.get("items", []))
        if not data.get("has_more"):
            break
        page_token = data.get("page_token")

    fields_data = api_get(token, f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields")
    field_names = [f.get("field_name", "") for f in fields_data.get("items", [])]

    parts = [f"## Search Results ({len(all_records)} records)\n"]
    if field_names:
        parts.append("| record_id | " + " | ".join(field_names) + " |")
        parts.append("| --- | " + " | ".join(["---"] * len(field_names)) + " |")
        for record in all_records:
            rid = record.get("record_id", "")
            rf = record.get("fields", {})
            cells = [sanitize_cell(extract_bitable_value(rf.get(fn))) for fn in field_names]
            parts.append(f"| {rid} | " + " | ".join(cells) + " |")
    else:
        parts.append(json.dumps(all_records, ensure_ascii=False, indent=2))
    parts.append("")

    _output("\n".join(parts), args.output)


# ── Subcommand: create ───────────────────────────────────────────

def cmd_create(args):
    token = get_auth()
    info = resolve_url(args.url, token)
    app_token = info["app_token"]
    table_id = args.table or info.get("table_id")
    if not table_id:
        print("Error: --table required for create.", file=sys.stderr)
        sys.exit(1)

    records_input = json.loads(args.records)
    if isinstance(records_input, dict):
        records_input = [records_input]

    body = {"records": [{"fields": r} for r in records_input]}
    path = f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
    result = api_post(token, path, body)

    created = result.get("records", [])
    print(f"Created {len(created)} record(s).", file=sys.stderr)
    for r in created:
        print(f"  record_id: {r.get('record_id', 'N/A')}")


# ── Subcommand: update ───────────────────────────────────────────

def cmd_update(args):
    token = get_auth()
    info = resolve_url(args.url, token)
    app_token = info["app_token"]
    table_id = args.table or info.get("table_id")
    if not table_id:
        print("Error: --table required for update.", file=sys.stderr)
        sys.exit(1)
    if not args.record_id:
        print("Error: --record-id required for update.", file=sys.stderr)
        sys.exit(1)

    fields = json.loads(args.fields)
    path = f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{args.record_id}"
    result = api_put(token, path, {"fields": fields})

    record = result.get("record", {})
    print(f"Updated record_id: {record.get('record_id', args.record_id)}")


# ── Subcommand: delete ───────────────────────────────────────────

def cmd_delete(args):
    token = get_auth()
    info = resolve_url(args.url, token)
    app_token = info["app_token"]
    table_id = args.table or info.get("table_id")
    if not table_id:
        print("Error: --table required for delete.", file=sys.stderr)
        sys.exit(1)
    if not args.record_ids:
        print("Error: --record-ids required (comma-separated).", file=sys.stderr)
        sys.exit(1)

    ids = [rid.strip() for rid in args.record_ids.split(",")]
    path = f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete"
    api_post(token, path, {"records": ids})
    print(f"Deleted {len(ids)} record(s).")


# ── Output helper ────────────────────────────────────────────────

def _output(content: str, filepath: str = None):
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Written to {filepath}", file=sys.stderr)
    else:
        print(content)


# ── CLI ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Feishu Data Tool — read/write spreadsheets and bitables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Subcommand")

    # read
    p_read = sub.add_parser("read", help="Read sheet or bitable content")
    p_read.add_argument("--url", required=True, help="Feishu URL (sheet/wiki/base)")
    p_read.add_argument("--table", help="Bitable table_id (reads all if omitted)")
    p_read.add_argument("--output", "-o", help="Output file path")
    p_read.set_defaults(func=cmd_read)

    # list-tables
    p_lt = sub.add_parser("list-tables", help="List tables in a bitable")
    p_lt.add_argument("--url", required=True, help="Feishu bitable URL")
    p_lt.add_argument("--output", "-o", help="Output file path")
    p_lt.set_defaults(func=cmd_list_tables)

    # search
    p_search = sub.add_parser("search", help="Search bitable records with filter")
    p_search.add_argument("--url", required=True, help="Feishu bitable URL")
    p_search.add_argument("--table", help="Bitable table_id")
    p_search.add_argument("--filter", help='Filter JSON, e.g. \'{"conjunction":"and","conditions":[...]}\'')
    p_search.add_argument("--output", "-o", help="Output file path")
    p_search.set_defaults(func=cmd_search)

    # create
    p_create = sub.add_parser("create", help="Batch create records")
    p_create.add_argument("--url", required=True, help="Feishu bitable URL")
    p_create.add_argument("--table", help="Bitable table_id")
    p_create.add_argument("--records", required=True, help='JSON: single object or array of {field: value}')
    p_create.set_defaults(func=cmd_create)

    # update
    p_update = sub.add_parser("update", help="Update a single record")
    p_update.add_argument("--url", required=True, help="Feishu bitable URL")
    p_update.add_argument("--table", help="Bitable table_id")
    p_update.add_argument("--record-id", required=True, help="Record ID to update")
    p_update.add_argument("--fields", required=True, help='JSON: {field: new_value, ...}')
    p_update.set_defaults(func=cmd_update)

    # delete
    p_delete = sub.add_parser("delete", help="Batch delete records")
    p_delete.add_argument("--url", required=True, help="Feishu bitable URL")
    p_delete.add_argument("--table", help="Bitable table_id")
    p_delete.add_argument("--record-ids", required=True, help="Comma-separated record IDs")
    p_delete.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal: {e}", file=sys.stderr)
        sys.exit(1)
