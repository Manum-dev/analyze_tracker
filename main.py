
import typer
import sys
import os

# Ensure project root is in sys.path to allow running directly


from typing import Optional
from cleanliness import Observability
from analyzer import Analyzer

app = typer.Typer(help="Analyze Tracker - AI powered text analysis")

@app.command()
def analyze(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Direct text input to analyze"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="File path to analyze"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable verbose debug logging")
):
    """
    Analyze text for metrics and sentiment.
    """
    # 1. Initialize Observability infrastructure
    # This ensures that even startup errors are captured if possible (though here we init it first)
    obs = Observability(debug=debug)
    logger = obs.get_logger("cli")
    
    logger.info("cli_started", debug_mode=debug)

    # 2. Input Validation
    if not text and not file:
        logger.warning("no_input_provided")
        typer.echo("Please provide either --text or --file")
        raise typer.Exit(code=1)
    
    if text and file:
        logger.warning("multiple_inputs_provided")
        typer.echo("Please provide either --text or --file, not both")
        raise typer.Exit(code=1)

    input_data = text
    source = "text_input"

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
        typer.echo("-" * 20)
        typer.echo(f"Source: {source}")
        typer.echo(f"metrics: {result.word_count} words, {result.sentence_count} sentences")
        
        if result.sentiment_score is not None:
             # rich formatting could be nice here, but keeping it simple for now
            mood = "Neutral"
            if result.sentiment_score > 0.1: mood = "Positive"
            if result.sentiment_score < -0.1: mood = "Negative"
            typer.echo(f"Sentiment: {result.sentiment_score} ({mood})")
            typer.echo(f"Keywords: {', '.join(result.keywords)}")
        else:
            typer.echo("Sentiment: N/A (API Analysis Skipped or Failed)")
            
        typer.echo("-" * 20)

    except Exception as e:
        logger.error("analysis_failed", error=str(e))
        typer.echo(f"An error occurred: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
