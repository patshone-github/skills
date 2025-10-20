---
name: ma-tracker-consulting-tech
description: Track and analyze M&A deals in consulting and tech services (£5-50m), generate weekly Excel reports with sector analysis
when_to_use: when user asks to track M&A deals, analyze acquisition activity in consulting/tech services, generate M&A reports, or monitor PE/strategic buyer activity in mid-market (£5-50m) tech/consulting sectors
metadata:
  version: "1.0.0"
  dependencies: "pandas>=2.0.0, openpyxl>=3.1.0, feedparser>=6.0.0, python-dateutil>=2.8.0"
---

# M&A Tracker for Consulting & Technology Services

## Overview

This Skill enables Claude to track, analyze, and report on merger and acquisition activity in the consulting and technology services sectors, with a focus on mid-market deals (£5-50m turnover).

## When to Use This Skill

Claude should use this Skill when users ask about:
- Tracking M&A activity in consulting or technology services
- Creating weekly or monthly M&A reports
- Analyzing acquisition trends in these sectors
- Monitoring private equity or strategic buyer activity
- Identifying deals involving specific technologies (AI, cloud, cybersecurity)

Example prompts that should trigger this Skill:
- "Track consulting M&A deals from the past week"
- "Create an M&A report for tech services acquisitions"
- "Show me PE activity in consulting firms"
- "Analyze recent cybersecurity acquisitions"

## How to Execute

### Basic Usage
```python
# Run with default settings (last 7 days)
exec(open('ma_tracker.py').read())

# Or via command line
python ma_tracker.py
```

### With Parameters
```python
# Custom lookback period
python ma_tracker.py --days 14

# Specific sector focus
python ma_tracker.py --sector "Cybersecurity"

# Output to specific location
python ma_tracker.py --output "weekly_report.xlsx"
```

## How This Skill Works

This skill uses a **web_fetch-first architecture**. ALL RSS feeds must be retrieved using Claude's WebFetch tool before processing. This approach avoids HTTP 403 errors and other blocking mechanisms used by RSS providers.

### Workflow

1. **Claude fetches feeds** using WebFetch tool for each feed in the OPML file:
   ```
   WebFetch(url="https://uktechexits.news/feed", prompt="Return raw RSS XML content")
   ```

2. **Cache the fetched content**:
   ```bash
   python fetch_blocked_feeds.py --feed-name "uktechexits" --content-file /tmp/feed.xml
   ```

3. **Process all cached feeds**:
   ```bash
   python ma_tracker.py --opml data/rss_feeds.opml
   ```

The tracker automatically looks for cached versions of each feed listed in the OPML file. Feeds not found in the cache are skipped with a warning.

### Configuration

The tracker is controlled by `config.json`:

```json
{
    "deal_filters": {
        "turnover_range_millions": {"min": 5, "max": 50},
        "include_undisclosed": true,
        "days_lookback": 7,
        "sectors": ["Consulting", "IT Services", "Digital Transformation"]
    },
    "blocked_feeds": {
        "cache_directory": "/tmp/ma_tracker_feeds"
    }
}
```

**Note:** The `cache_directory` setting determines where the tracker looks for pre-fetched feed files.

## Data Sources

RSS feeds are defined in `data/rss_feeds.opml`:
- Consultancy.eu/uk M&A news
- Financial Times M&A section
- Reuters Deals
- Grant Thornton Insights
- Industry-specific newsletters

## Output Structure

The Skill generates an Excel file with multiple sheets:

1. **Deal Tracker** - Complete list of all deals
2. **Executive Summary** - Key metrics and highlights
3. **Sector Analysis** - Breakdown by industry vertical
4. **Buyer Analysis** - PE vs Strategic activity
5. **Technology Trends** - Emerging tech focuses
6. **Geographic Analysis** - Regional distribution
7. **Monthly Trends** - Time series analysis

## Key Features

- **Smart Extraction**: Automatically identifies buyer, target, value, and rationale
- **Classification**: Categorizes buyer type (PE/Strategic) and sector
- **Filtering**: Focuses on relevant deal sizes and sectors
- **Trend Analysis**: Tracks patterns over time
- **Alert System**: Flags high-priority deals

## Dependencies

All required Python packages are listed in `requirements.txt`:
- pandas (data processing)
- openpyxl (Excel generation)
- feedparser (RSS parsing)
- python-dateutil (date handling)

## Files Structure

```
ma-tracker-consulting-tech/
├── Skill.md              # This file
├── ma_tracker.py         # Main execution script
├── config.json           # Configuration
├── requirements.txt      # Python dependencies
└── data/
    └── rss_feeds.opml   # RSS feed sources
```

## Example Output

When executed, the Skill produces output like:

```
🔍 Processing RSS feeds...
✓ Found deal: Accenture → Cloud Consulting Ltd
✓ Found deal: PE Firm → Data Analytics Co
📊 Generated report: MA_Tracker_20251020.xlsx
   Total deals: 8
   Date range: 2025-10-13 to 2025-10-20
```

## Error Handling

The Skill handles common issues:
- RSS feed timeouts (retries with backoff)
- Missing deal values (marks as "Undisclosed")
- Ambiguous entities (flags for review)
- Duplicate deals (deduplication logic)

## Customization

Users can modify:
- Deal size ranges in config.json
- Sectors to track
- RSS feed sources in OPML file
- Alert criteria
- Output format preferences

## Support

For issues:
1. Check RSS feed accessibility
2. Verify Python dependencies are installed
3. Review config.json settings
4. Ensure proper date formats

## Version History

- 1.0.0 - Initial release with core tracking capabilities
