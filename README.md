# KOL Sentiment MCP

A Model Context Protocol (MCP) implementation for Key Opinion Leader sentiment analysis using the Masa AI API.

## Overview

KOL Sentiment MCP provides a standardized interface for AI assistants to analyze Key Opinion Leaders (KOLs) on social media platforms. It leverages the Masa AI API for powerful semantic search and data retrieval, allowing for sentiment analysis, topic extraction, and trend identification without direct API access.

## Features

- Search for KOL content across platforms
- Analyze sentiment of KOL posts
- Extract trending topics from KOL content
- Generate comprehensive KOL sentiment analysis
- Identify trends across multiple KOLs
- Support for both live and indexed (historical) data
- Secure and rate-limited API access
- Detailed logging and error handling

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/olaxbt/kol-sentiment-mcp.git
   cd kol-sentiment-mcp
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file to add your Masa API key and other settings.

## Usage

### Starting the Server

```bash
python run.py
```

The server will start on the port specified in your `.env` file (default: 5000).

### API Endpoints

- `GET /` - Welcome page with service information
- `GET /health` - Health check endpoint
- `GET /api/mcp/ping` - MCP service health check
- `POST /api/mcp/query` - Main MCP query endpoint

### MCP Actions

The KOL Sentiment MCP supports the following actions:

1. `kol.search` - Search for KOL content
2. `kol.sentiment` - Analyze sentiment of KOL content
3. `kol.topics` - Extract topics from KOL content
4. `kol.insights` - Get comprehensive insights about a KOL
5. `kol.trends` - Analyze trends across multiple KOLs

### Example Queries

#### Search for KOL Content

```json
{
  "id": "request123",
  "action": "kol.search",
  "params": {
    "query": "cryptocurrency",
    "kol_username": "elonmusk",
    "search_type": "indexed",
    "max_results": 10
  }
}
```

#### Analyze KOL Sentiment

```json
{
  "id": "request123",
  "action": "kol.sentiment",
  "params": {
    "query": "AI",
    "kol_username": "elonmusk",
    "search_type": "indexed",
    "max_results": 20
  }
}
```

#### Get Comprehensive KOL Insights

```json
{
  "id": "request123",
  "action": "kol.insights",
  "params": {
    "username": "elonmusk",
    "query": "",
    "search_type": "indexed",
    "max_results": 20
  }
}
```

#### Analyze Trends Across Multiple KOLs

```json
{
  "id": "request123",
  "action": "kol.trends",
  "params": {
    "usernames": ["elonmusk", "VitalikButerin", "SBF_FTX"],
    "query": "blockchain",
    "search_type": "indexed",
    "max_results_per_kol": 10
  }
}
```

## Development

### Project Structure

```
kol-sentiment-mcp/
├── app/
│   ├── handlers/        # Action handlers
│   ├── routes/          # API routes
│   ├── services/        # Core services
│   ├── templates/       # HTML templates
│   └── utils/           # Utilities
├── logs/                # Log files
├── tests/               # Test cases
├── .env                 # Environment variables
├── .env.example         # Example environment file
├── requirements.txt     # Dependencies
├── run.py               # Main entry point
└── README.md            # Documentation
```

## License

MIT

## Acknowledgements

- [Masa AI API](https://developers.masa.ai/) for X/Twitter data retrieval
- [Model Context Protocol](https://github.com/anthropics/model-context-protocol) for standardized AI interaction 