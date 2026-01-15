# Analyze Tracker - Product Requirement Document

## 1. Product Overview
**Name**: `analyze_tracker`
**Elevator Pitch**: A CLI tool that leverages Google Gemini AI to analyze text files for sentiment and metrics, providing automated insights and persistent tracking.
**Value Proposition**: Simplifies text analysis by combining AI-powered sentiment detection with standard metrics (word count) and local historical tracking.

## 2. Functional Specifications (MVP)

### 2.1 Inputs
- **CLI Arguments**: The tool accepts input via command-line arguments.
- **Source**:
    - File path (e.g., `./run.sh --file data/sample.txt`)
    - Direct text input (e.g., `./run.sh --text "I love this project"`)

### 2.2 Processing
- **AI Integration**: Uses `google-generativeai` (Gemini Pro model).
- **Analysis Logic**:
    1.  **Sentiment Analysis**: Returns a floating-point score from `-1.0` (Very Negative) to `+1.0` (Very Positive).
    2.  **Keyword Extraction**: Identifies top 3-5 main keywords/topics.
    3.  **Basic Metrics**: Calculates word count, character count, and sentence count locally (or via AI if requested).

### 2.4 Privacy & Data Handling
- **Data Transmission**: Text content is sent to Google's Gemini API for analysis. The tool does not store this data on external servers controlled by us, but Google's data retention policies apply.
- **Local Storage**: Analysis results are stored locally in `analyze_tracker.db` or `db.json`.
- **User Control**:
    - Users can use the `--no-history` flag to perform analysis *without* saving the input/output to the local database.
    - API usage requires an explicit API Key, reinforcing user responsibility.

### 2.3 Outputs
- **Console Display**: Formatted, color-coded output showing the analysis results.
- **Persistence**:
    - Results are saved to a local SQLite database (`analyze_tracker.db`) or structured JSON (`db.json`) for history tracking.
    - Fields: `timestamp`, `filename/source`, `sentiment_score`, `keywords`, `word_count`.

## 3. Non-Functional Requirements
- **Performance**: API calls should be handled efficiently; user should see a loading indicator.
- **Reliability**: Graceful handling of API errors (e.g., "Quota exceeded") and Network timeouts.
- **Security**: API Keys must be loaded from environment variables (`.env`), never hardcoded.
- **Usability**: Clean CLI help messages (`--help`) and intuitive command structure.

## 4. Technical Constraints
- **Language**: Python 3.10+
- **AI Provider**: Google Gemini API
- **Dependencies**: `google-generativeai`, `python-dotenv`, `typer` or `argparse`, `rich` (for UI).
- **Data Store**: SQLite (Preferred for structure) or JSON.

## 5. Future Roadmap (Post-MVP)
- Batch processing of multiple files.
- Export results to CSV/PDF.
- Visual charts of sentiment history.
