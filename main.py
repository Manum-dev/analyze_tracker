
import typer
import sys
import os

# Ensure project root is in sys.path to allow running directly


from typing import Optional
from cleanliness import Observability
from analyzer import Analyzer
from db import Database

app = typer.Typer(help="Analyze Tracker - AI powered text analysis")

@app.command()
def analyze(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Direct text input to analyze"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="File path to analyze"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable verbose debug logging")
):
    """
    Analyze text for metrics and sentiment using Gemini API.
    
    This command requires a valid GEMINI_API_KEY environment variable.
    Results will be saved to a local JSON file (analysis_history.json).
    """
    # 1. Initialize Observability infrastructure
    # This ensures that even startup errors are captured if possible (though here we init it first)
    obs = Observability(debug=debug)
    logger = obs.get_logger("cli")
    
    logger.info("cli_started", debug_mode=debug)

    # 2. Input Validation
    if not text and not file:
        # Interactive mode as requested
        text = typer.prompt("Inserisci il testo da analizzare")
    
    if text and file:
        logger.warning("multiple_inputs_provided")
        typer.echo("Please provide either --text or --file, not both")
        raise typer.Exit(code=1)

    input_data = text
    source = text

    # Handle file input
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                input_data = f.read()
            source = f"file:{file}"
            logger.debug("file_read_success", filename=file)
        except Exception as e:
            logger.error("file_read_error", filename=file, error=str(e))
            typer.echo(f"Error reading file: {e}")
            raise typer.Exit(code=1)

    # 3. Perform Analysis
    try:
        analyzer = Analyzer()
        # Switching to full AI analysis
        # Note: This requires GEMINI_API_KEY in .env
        result = analyzer.analyze_with_gemini(input_data)
        
        logger.info("analysis_success", source=source, result=result)
        
        # 4. Display Output
        typer.echo("=" * 40)
        typer.echo(f"  ANALYZE TRACKER REPORT")
        typer.echo("=" * 40)
        typer.echo(f"Source: {source}")
        
        # Summary Section
        if result.summary:
            typer.echo(f"\n[SUMMARY]\n{result.summary}")
            
        # Metrics Section
        typer.echo(f"\n[METRICS]\nWords: {result.word_count} | Sentences: {result.sentence_count} | Chars: {result.char_count}")

        # Sentiment Section
        if result.sentiment_label:
            typer.echo(f"\n[SENTIMENT]\n{result.sentiment_label.upper()} (Confidence: {result.sentiment_confidence})")
        
        # Keywords Section
        if result.keywords:
           typer.echo(f"\n[KEYWORDS]\n{', '.join(result.keywords)}")
           
        if not result.sentiment_label and not result.summary:
             typer.echo("\n(Note: Full AI analysis data missing or failed)")
            
        # 4. Save to DB
        try:
            db = Database()
            row_id = db.save_result(source, result)
            typer.echo(f"\nResult saved to database (ID: {row_id})")
        except Exception as db_err:
            logger.error("db_save_failed_main", error=str(db_err))
            typer.echo(f"\nWarning: Failed to save result to database: {db_err}")

        typer.echo("-" * 20)

    except Exception as e:
        logger.error("analysis_failed", error=str(e))
        typer.echo(f"An error occurred: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
