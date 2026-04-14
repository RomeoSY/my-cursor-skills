---
name: feishu-mcp
description: >-
  Feishu (Lark) MCP server setup guide. Configures document-centric capabilities
  (docx read/write, wiki, folder, whiteboard, image, search) via the feishu-mcp
  and @larksuiteoapi/lark-mcp npm packages.
---

# Feishu MCP Server

MCP server configuration for Feishu document-centric operations. For spreadsheet/bitable data operations, use the companion **feishu-data** skill instead.

## Capability Map

| Need | Tool |
|------|------|
| Read/edit **document** (docx, wiki page) | **feishu-mcp** |
| Search documents | **feishu-mcp** `search_feishu_documents` |
| Folder listing / creation | **feishu-mcp** |
| Whiteboard (PlantUML) | **feishu-mcp** |
| Image upload & bind | **feishu-mcp** |
| Read **spreadsheet** or **bitable** | **feishu-data** skill |
| Write/update/delete **bitable records** | **feishu-data** skill |

## Setup

### 1. Create a Feishu App

1. Go to [Feishu Open Platform](https://open.feishu.cn/app)
2. Create an internal app (企业自建应用)
3. Note the `App ID` and `App Secret`
4. Grant required permissions:
   - `docs:doc` / `docs:doc:readonly` — document read/write
   - `wiki:wiki` / `wiki:wiki:readonly` — wiki read/write
   - `drive:drive` — drive/folder operations
   - `bitable:bitable` — bitable read/write (for feishu-data)
   - `sheets:spreadsheet` — spreadsheet read (for feishu-data)

### 2. Configure MCP in Cursor

Add the following to `.cursor/mcp.json`:

```json
{
    "mcpServers": {
        "feishu-mcp": {
            "command": "npx",
            "args": ["-y", "feishu-mcp", "--stdio"],
            "env": {
                "FEISHU_APP_ID": "cli_a8ee6586f7f1900d",
                "FEISHU_APP_SECRET": "RaMHlWobT9ZVEfEqmTC9igVcFE1u6lwg"
            }
        },
        "lark-mcp": {
            "command": "npx",
            "args": [
                "-y",
                "@larksuiteoapi/lark-mcp",
                "mcp",
                "-a", "cli_a8ee6586f7f1900d",
                "-s", "RaMHlWobT9ZVEfEqmTC9igVcFE1u6lwg",
                "-t", "drive.v1.fileComment.list,drive.v1.fileComment.get,drive.v1.fileComment.batchQuery,drive.v1.fileCommentReply.list,bitable.v1.appTable.list,bitable.v1.appTableField.list,bitable.v1.appTableRecord.search,sheets.v3.spreadsheet.get,sheets.v3.spreadsheetSheet.query,sheets.v3.spreadsheetSheet.get,sheets.v3.spreadsheetSheet.find"
            ]
        }
    }
}
```

### 3. Set Environment Variables (for feishu-data skill)

The feishu-data companion skill reads `FEISHU_APP_ID` and `FEISHU_APP_SECRET` from environment variables. Set them in your shell profile or `.env` file:

```powershell
$env:FEISHU_APP_ID = "cli_a8ee6586f7f1900d"
$env:FEISHU_APP_SECRET = "RaMHlWobT9ZVEfEqmTC9igVcFE1u6lwg"
```

## Available MCP Tools

### feishu-mcp (npm: `feishu-mcp`)

| Tool | Description |
|------|-------------|
| `get_feishu_document_info` | Get document metadata |
| `get_feishu_document_blocks` | Read document content blocks |
| `batch_create_feishu_blocks` | Add blocks to a document |
| `batch_update_feishu_block_text` | Update block text content |
| `delete_feishu_document_blocks` | Delete blocks from a document |
| `create_feishu_document` | Create a new document |
| `create_feishu_table` | Create a table in a document |
| `search_feishu_documents` | Search documents by keyword |
| `get_feishu_folder_files` | List files in a folder |
| `create_feishu_folder` | Create a folder |
| `get_feishu_root_folder_info` | Get root folder info |
| `get_feishu_whiteboard_content` | Read whiteboard content |
| `fill_whiteboard_with_plantuml` | Write PlantUML to whiteboard |
| `get_feishu_image_resource` | Download image from document |
| `upload_and_bind_image_to_block` | Upload and insert image |

### lark-mcp (npm: `@larksuiteoapi/lark-mcp`)

Provides additional APIs for comments, bitable schema, and spreadsheet operations. Use the `-t` flag to select specific API scopes.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Auth failed` | Check App ID / Secret are correct |
| `99991663` Permission denied | Add the app as a collaborator on the document |
| `1310213` Insufficient scope | Add required permissions in Feishu admin console |
| MCP server not starting | Run `npx feishu-mcp --stdio` manually to check errors |
| Chinese characters garbled | Ensure `PYTHONIOENCODING=utf-8` for feishu-data |

## Division of Labor

- **feishu-mcp**: Document-centric (docx CRUD, wiki, folder, whiteboard, image, search)
- **feishu-data**: Data-centric (spreadsheet read, bitable CRUD with record-level operations)

Both share the same Feishu app credentials.
