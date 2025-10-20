# M&A Tracker - Consulting & Tech Services

## Overview

An automated M&A (Mergers & Acquisitions) tracking system that monitors consulting and technology services deals, focusing on mid-market transactions (£5-50m turnover range).

## Features

- 📰 **RSS Feed Monitoring**: Tracks 13+ industry news sources
- 💰 **Deal Filtering**: Focuses on £5-50m turnover range
- 📊 **Excel Reports**: Comprehensive multi-sheet analysis
- 🎯 **Sector Analysis**: Breakdown by industry vertical  
- 🔔 **Alert System**: Flags high-priority deals
- 🌍 **Geographic Tracking**: Regional distribution analysis

## Quick Start

```bash
# Basic usage (last 7 days)
python ma_tracker.py

# Custom lookback period
python ma_tracker.py --days 14

# Specific sector focus
python ma_tracker.py --sector "Cybersecurity"

# Custom output location
python ma_tracker.py --output "weekly_report.xlsx"
```

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Test the installation
python test_skill.py
```

## Configuration

Edit `config.json` to customize:

- **Deal filters**: Size range, sectors, geography
- **Data sources**: RSS feeds, refresh intervals
- **Buyer classification**: PE vs Strategic indicators
- **Output settings**: File location, included sheets
- **Alert criteria**: Thresholds and notification settings

## Output

The skill generates an Excel file with multiple sheets:

1. **Deal Tracker** - Complete list of all deals
2. **Executive Summary** - Key metrics and highlights
3. **Sector Analysis** - Breakdown by industry vertical
4. **Buyer Analysis** - PE vs Strategic activity
5. **Technology Trends** - Emerging tech focuses
6. **Geographic Analysis** - Regional distribution

## Data Sources

RSS feeds are configured in `data/rss_feeds.opml`:
- Consultancy.eu/uk M&A news
- Financial Times M&A section
- Reuters Deals
- Industry newsletters
- PE and investment news

## Validation

```bash
# Check spec compliance
python validate_spec.py

# Run tests
python test_skill.py
```

## Version

Current version: 1.0.0

## License

MIT License - See parent repository for details
