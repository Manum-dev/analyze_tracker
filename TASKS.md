# Analyze Tracker - Implementation Plan

## Phase 1: Project Setup
- [ ] Initialize Python project (Python 3.10+)
- [ ] Create virtual environment
- [ ] Install dependencies:
    - `google-generativeai`
    - `python-dotenv`
    - `typer` (or argparse)
    - `rich`
- [ ] Set up `.env` for `GEMINI_API_KEY`
- [ ] Create basic directory structure

## Phase 2: Core Logic Implementation
- [ ] Implement Basic Metrics Calculator
    - [ ] Word count
    - [ ] Character count
    - [ ] Sentence count
- [ ] Implement Gemini AI Integration
    - [ ] Setup client with API key
    - [ ] specific prompt for sentiment analysis (-1.0 to +1.0) and keyword extraction
    - [ ] Error handling for API calls

## Phase 3: CLI Development
- [ ] Implement CLI with `typer`
- [ ] Add arguments:
    - [ ] `--file` for file path
    - [ ] `--text` for direct input
- [ ] Implement Console Output using `rich`
    - [ ] Show loading indicator during API call
    - [ ] Display formatted results (Sentiment, Keywords, Metrics)

## Phase 4: Data Persistence & Features
- [ ] Database Setup (SQLite/JSON)
    - [ ] Schema: `timestamp`, `source`, `sentiment_score`, `keywords`, `word_count`
- [ ] Implement Save Functionality
- [ ] Add `--no-history` flag to skip saving

## Phase 5: Testing & Refinement
- [ ] Test with sample text files
- [ ] Test direct text input
- [ ] Verify error handling (Network, API Quota)
- [ ] Final code cleanup and documentation
