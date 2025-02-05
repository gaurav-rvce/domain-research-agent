# VC Research AI Agent

An intelligent AI agent designed for Venture Capitalists to conduct comprehensive market research and company analysis.

## Features

- Domain-specific research capabilities
- Automated company discovery and analysis
- Product line investigation
- Detailed company profiles in markdown format
- Domain summary with potential opportunities
- Multi-step LLM planning and validation
- Web scraping and information extraction

## Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```
2. Access the API documentation at `http://localhost:8000/docs`

## Project Structure

```
.
├── README.md
├── requirements.txt
├── main.py                 # FastAPI application
├── agent/
│   ├── __init__.py
│   ├── planner.py         # LLM planning module
│   ├── validator.py       # Plan validation module
│   ├── executor.py        # Plan execution module
│   ├── tools/            # Function calling tools
│   │   ├── __init__.py
│   │   ├── web_search.py
│   │   ├── web_scraper.py
│   │   └── file_writer.py
│   └── prompts/          # LLM prompt templates
│       ├── __init__.py
│       ├── planning.py
│       └── validation.py
└── .env                   # Environment variables
```

## API Endpoints

- `POST /research`: Start a new research task
  - Input: Domain to research
  - Output: Job ID for tracking progress

- `GET /research/{job_id}`: Get research status and results
  - Output: Current status and available results

## License

MIT License 