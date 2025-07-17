# Google Drive server

This MCP server integrates with Google Drive to allow listing, reading, and searching over files.

## Components

### Tools

- **search**
  - Search for files in Google Drive
  - Input: `query` (string): Search query
  - Returns file names and MIME types of matching files

### Resources

The server provides access to Google Drive files:

- **Files** (`gdrive:///<file_id>`)
  - Supports all file types
  - Google Workspace files are automatically exported:
    - Docs → Markdown
    - Sheets → CSV
    - Presentations → Plain text
    - Drawings → PNG
  - Other files are provided in their native format

## Getting started

1. [Create a new Google Cloud project](https://YOUR-CREDENTIALS@YOUR-DOMAIN/server-gdrive"
      ]
    }
  }
}
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
