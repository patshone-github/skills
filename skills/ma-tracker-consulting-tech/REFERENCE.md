# Technical Reference - M&A Tracker Skill

## Data Extraction Patterns

### Company Name Extraction
The skill uses regex patterns to identify buyer and target companies:

```python
patterns = [
    r'([A-Z][A-Za-z\s&]+?)\s+(?:acquires?|buys?)\s+([A-Z][A-Za-z\s&]+)',
    r'([A-Z][A-Za-z\s&]+?)\s+(?:to acquire|to buy)\s+([A-Z][A-Za-z\s&]+)',
    r'([A-Z][A-Za-z\s&]+?)\s+(?:merger with)\s+([A-Z][A-Za-z\s&]+)'
]
```

### Deal Value Extraction
Identifies monetary values in various formats:
- £25m, £25 million
- $50M, $50 million  
- €30m, €30 million
- 25 million (currency inferred from context)

### Buyer Type Classification

**Private Equity Indicators:**
- "private equity", "PE firm", "PE-backed"
- "portfolio company", "investment firm"
- Company names ending in "Partners", "Capital", "Holdings"

**Strategic Buyer Indicators:**
- "strategic acquisition", "synergies"
- Operating companies in same sector
- No PE indicators present

## Sector Taxonomy

### Primary Sectors
- **Consulting**: Management, strategy, operational consulting
- **IT Services**: Managed services, implementation, integration
- **Digital Transformation**: Digital strategy, transformation programs
- **Cloud & Infrastructure**: Cloud migration, infrastructure services
- **Cybersecurity**: Security services, compliance, risk management
- **Data & Analytics**: BI, data science, analytics consulting
- **AI & Automation**: AI implementation, RPA, intelligent automation

### Technology Keywords Tracked

**Tier 1 (Primary Focus):**
- Artificial Intelligence / AI
- Cloud Computing
- Data Analytics
- Cybersecurity
- Digital Transformation

**Tier 2 (Secondary):**
- SaaS, ERP, CRM
- Blockchain, IoT
- DevOps, Agile
- RPA, Machine Learning

## RSS Feed Sources

### Consultancy-Focused
- Consultancy.eu - European consulting M&A
- Consultancy.uk - UK consulting M&A
- Source Global Research - Market intelligence

### Financial News
- Financial Times - M&A section
- Reuters - Deals coverage
- Bloomberg (if available)

### PE & Investment
- PE Hub - Private equity deals
- PitchBook (requires subscription)
- Mergermarket (requires subscription)

### Technology
- TechCrunch - Tech M&A
- Sifted.eu - European tech
- Information Week

## Alert Logic

### High Priority Alerts
Triggered when ALL conditions met:
1. Deal value > £25m OR undisclosed
2. Buyer is key competitor OR PE firm
3. Target has strategic technology

### Medium Priority Alerts  
Triggered when ANY conditions met:
1. New PE entrant to market
2. Roll-up strategy detected (3+ deals by same buyer)
3. Cross-border transaction

### Low Priority Alerts
- All other deals matching basic filters

## Data Quality Scoring

Each extracted deal receives a confidence score (0-1):

```python
score = 1.0
if 'rumor' in text: score *= 0.8
if 'undisclosed' in text: score *= 0.9
if missing_buyer_or_target: score *= 0.7
if no_sector_match: score *= 0.85
```

## Excel Output Schema

### Sheet 1: Deal Tracker
| Column | Type | Description |
|--------|------|-------------|
| Date | Date | Announcement date |
| Buyer | String | Acquiring company |
| Target | String | Company acquired |
| Deal_Value_M | Float | Value in millions |
| Value_Range | String | Categorized range |
| Buyer_Type | String | PE/Strategic |
| Sector | String | Primary sector |
| Technology_Focus | String | Key technologies |
| Geography | String | Region |
| Link | URL | Source article |
| Confidence | Float | Data quality score |

### Sheet 2: Executive Summary
- Total deal count
- Total disclosed value
- Average deal size
- Date range covered
- Most active buyer
- Hottest sector
- Key technology trends

## Advanced Configuration

### Custom Sector Definitions
Add to config.json:
```json
"custom_sectors": {
    "FinTech Consulting": ["payments", "banking tech", "regtech"],
    "Healthcare IT": ["health tech", "medical software", "telehealth"]
}
```

### Geographic Mapping
Extend in config.json:
```json
"geographic_mapping": {
    "Nordics": ["sweden", "norway", "denmark", "finland"],
    "DACH": ["germany", "austria", "switzerland"]
}
```

### Value Range Customization
Modify in config.json:
```json
"value_ranges": [
    {"label": "<£10m", "min": 0, "max": 10},
    {"label": "£10-30m", "min": 10, "max": 30},
    {"label": "£30-75m", "min": 30, "max": 75},
    {"label": ">£75m", "min": 75, "max": null}
]
```

## Performance Optimization

### RSS Feed Processing
- Concurrent feed fetching (if >10 feeds)
- Cache feed results for 1 hour
- Skip feeds with >5 consecutive failures

### Data Processing
- Batch process deals before Excel generation
- Use DataFrame operations vs loops
- Implement incremental updates for large datasets

## Troubleshooting

### Common Issues

**No deals found:**
- Check RSS feed URLs are accessible
- Verify date range (increase days_lookback)
- Review sector filters (may be too restrictive)

**Extraction errors:**
- Enable debug logging in config.json
- Check regex patterns match article format
- Verify text encoding (UTF-8 expected)

**Excel generation fails:**
- Ensure openpyxl is installed
- Check disk space for output
- Verify write permissions

### Debug Mode
Enable in config.json:
```json
"debug": {
    "enabled": true,
    "log_level": "DEBUG",
    "save_raw_feeds": true,
    "export_extraction_details": true
}
```

## Integration Points

### Email Notifications
```python
# Add to config.json
"notifications": {
    "email": {
        "enabled": true,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "from_address": "ma-tracker@company.com",
        "to_addresses": ["team@company.com"]
    }
}
```

### Database Storage
```python
# Add to config.json  
"database": {
    "enabled": true,
    "type": "postgresql",
    "connection": "postgresql://user:pass@localhost/ma_tracker"
}
```

### API Endpoints
Future enhancement to expose as REST API:
- GET /deals - List recent deals
- GET /deals/{id} - Get specific deal
- GET /reports/weekly - Generate weekly report
- GET /analytics/trends - Get trend data

## Maintenance

### Weekly Tasks
- Review RSS feed health
- Validate extraction accuracy
- Update sector definitions if needed

### Monthly Tasks
- Analyze missed deals
- Refine extraction patterns
- Update technology keywords
- Review and adjust value ranges

### Quarterly Tasks
- Full accuracy audit
- Performance optimization
- Feature enhancement planning
- Stakeholder feedback integration
