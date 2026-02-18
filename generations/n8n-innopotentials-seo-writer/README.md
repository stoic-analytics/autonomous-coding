# n8n SEO Writer Workflow

An n8n workflow automation that transforms external URLs and PDF documents into SEO-optimized WordPress blog posts for the DACH region (Germany, Austria, Switzerland).

## Overview

This workflow automates the content creation process:

1. **Input**: Client enters source URLs and optional PDFs in Google Sheets
2. **Parse**: Extract and clean content from URLs and PDFs
3. **Generate Content**: AI creates SEO-optimized blog posts using local Ollama
4. **Generate Image**: Create featured images using Flux Schnell
5. **Review**: Client reviews content in Google Sheets
6. **Publish**: Push approved content to WordPress as drafts

## Technology Stack

| Component | Technology |
|-----------|------------|
| Automation | n8n (self-hosted Docker) |
| LLM | Ollama (local) |
| Image Generation | Flux Schnell via ComfyUI (Apple Silicon M2 Max) |
| Input Interface | Google Sheets + Google Apps Script |
| Output | WordPress REST API |
| Notifications | Email (SMTP) |

## Prerequisites

- Docker and Docker Compose
- Ollama with a suitable model (llama3 or mistral)
- Flux Schnell set up via ComfyUI (for Apple Silicon)
- Google Cloud project with Sheets API enabled
- WordPress site with Application Password
- SMTP credentials for email notifications

## Quick Start

1. Clone this repository
2. Run the initialization script:
   ```bash
   chmod +x init.sh
   ./init.sh
   ```
3. Update `.env` with your credentials
4. Open n8n at http://localhost:5680
5. Import the workflow from `workflow-exports/`
6. Configure credentials in n8n

## Google Sheets Structure

| Column | Type | Description |
|--------|------|-------------|
| ID | Auto | Row identifier |
| URL | Text | Source website URL (required) |
| PDF_Links | Text | Comma-separated PDF URLs (optional) |
| Language | Dropdown | German or English |
| Status | Text | Processing status |
| Error_Message | Text | Error details if failed |
| Generated_Title | Text | AI-generated title |
| Generated_Content | Text | AI-generated content |
| Generated_Keywords | Text | DACH SEO keywords |
| Generated_Categories | Text | Suggested categories |
| Generated_Tags | Text | Suggested tags |
| Image_URL | Text | Generated image URL |
| Approve | Button | Triggers publish workflow |
| WordPress_URL | Text | Published draft URL |
| Created_At | Timestamp | Creation time |
| Updated_At | Timestamp | Last update |

## Workflow Status Values

- **Pending**: New row, not yet processed
- **Processing**: Currently being processed
- **Ready for Review**: Content generated, awaiting approval
- **Approved**: Approved for publishing
- **Published**: Successfully published to WordPress
- **Failed**: Error occurred (see Error_Message)

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# n8n Configuration
N8N_HOST=localhost
N8N_PORT=5678

# Ollama Configuration
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3

# ComfyUI / Flux Configuration
COMFYUI_HOST=http://host.docker.internal:8188

# Google Sheets Configuration
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_SHEET_ID=your-sheet-id

# WordPress Configuration
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=your-app-password

# SMTP Configuration
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password
```

### n8n Credentials Setup

In n8n, configure the following credentials:

1. **Google Sheets OAuth2** - For reading/writing to the sheet
2. **WordPress** - Application Password authentication
3. **SMTP** - For failure notifications

## Error Handling

| Error Type | Action | Notification |
|------------|--------|--------------|
| URL unreachable | Status = Failed, Error logged | Yes |
| PDF parse failure | Status = Failed, Error logged | Yes |
| LLM timeout | Status = Failed, Error logged | Yes |
| Image generation failure | Continue without image | No |
| WordPress API error | Status = Failed, Error logged | Yes |

## Development

### Directory Structure

```
.
├── init.sh                 # Environment setup script
├── docker-compose.yml      # n8n Docker configuration
├── .env                    # Environment variables
├── .env.example           # Environment template
├── n8n-data/              # n8n persistent data
├── workflow-exports/       # n8n workflow JSON exports
├── google-apps-script/    # Google Apps Script code
├── docs/                  # Additional documentation
└── README.md              # This file
```

### Workflow Testing

1. Add a test row in Google Sheets
2. Monitor n8n execution at http://localhost:5678
3. Check Ollama logs for LLM processing
4. Verify WordPress draft creation
5. Check email delivery for notifications

## License

Private project for Innopotentials.
