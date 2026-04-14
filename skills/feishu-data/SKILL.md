---
name: feishu-data
description: >-
  Read and write Feishu spreadsheets (sheet) and bitable (multi-dimensional tables)
  via Feishu Open API. Use when you need to read/write sheet or bitable content,
  or when a Feishu document is blocked because the MCP only supports docx.
---

# Feishu Data Tool

Unified read/write tool for Feishu spreadsheets and bitables. Complements the feishu-mcp (which handles docx/wiki/whiteboard/folder/image).

## Capability Map

| Need | Tool |
|------|------|
| Read/edit **document** (docx, wiki page) | **feishu-mcp** (MCP tools) |
| Search documents | **feishu-mcp** `search_feishu_documents` |
| Folder/whiteboard/image | **feishu-mcp** |
| Read **spreadsheet** or **bitable** | **This skill** → `feishu_data.py read` |
| Write/update/delete **bitable records** | **This skill** → `feishu_data.py create/update/delete` |

## Prerequisites

- Python 3.8+, `requests` library
- Environment variables: `FEISHU_APP_ID` and `FEISHU_APP_SECRET`

## Subcommands

### read — Read sheet or bitable content

```bash
python scripts/feishu_data.py read --url "https://befriends.feishu.cn/wiki/xxxxx"
python scripts/feishu_data.py read --url "https://befriends.feishu.cn/sheets/shtcnXXX"
python scripts/feishu_data.py read --url "https://befriends.feishu.cn/wiki/xxx" --table tblXXX
python scripts/feishu_data.py read --url "..." -o result.md
```

Output: markdown tables with `record_id` column for bitables.

### list-tables — List tables in a bitable

```bash
python scripts/feishu_data.py list-tables --url "https://befriends.feishu.cn/wiki/xxxxx"
```

Output: table of `table_id | name | revision`.

### search — Search records with filter

```bash
python scripts/feishu_data.py search --url "..." --table tblXXX \
  --filter '{"conjunction":"and","conditions":[{"field_name":"状态","operator":"is","value":["进行中"]}]}'
```

Filter format follows [Feishu Bitable Search API](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/search).

### create — Batch create records

```bash
# Single record
python scripts/feishu_data.py create --url "..." --table tblXXX \
  --records '{"任务名称":"测试任务","状态":"待开始"}'

# Multiple records
python scripts/feishu_data.py create --url "..." --table tblXXX \
  --records '[{"任务名称":"任务A"},{"任务名称":"任务B"}]'
```

Field names must match the bitable column names exactly.

### update — Update a single record

```bash
python scripts/feishu_data.py update --url "..." --table tblXXX \
  --record-id recXXXXX \
  --fields '{"状态":"已完成","备注":"done"}'
```

### delete — Batch delete records

```bash
python scripts/feishu_data.py delete --url "..." --table tblXXX \
  --record-ids "recAAA,recBBB,recCCC"
```

## Wiki-mounted Bitables

For bitables accessed via wiki URLs (`/wiki/xxx`), the tool automatically resolves the wiki node to get the underlying `obj_token` (app_token). No extra steps needed.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `99991663` | App lacks permission for this doc | Add app as collaborator in doc settings |
| `1310213` / `131006` | Insufficient API permissions | Check app permissions in Feishu admin console |
| `1254607` | Field name mismatch in create/update | Use `list-tables` + `read` to check exact field names |
| `empty response` | Doc is not sheet/bitable type | Use feishu-mcp instead |

## Integration Notes

- `feishu_data.py` is the unified entry point with subcommands
- Auth via `FEISHU_APP_ID` + `FEISHU_APP_SECRET` environment variables
- Companion to `feishu-mcp` npm package (handles docx/wiki/folder/image)
