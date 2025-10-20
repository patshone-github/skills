#!/usr/bin/env python3
"""
M&A Deal Tracker Skill
Main module for tracking consulting and tech services M&A activity
"""

import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import pandas as pd
import feedparser
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
import ssl

# Configure SSL for feeds
ssl._create_default_https_context = ssl._create_unverified_context

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Deal:
    """Data class for M&A deal information"""
    date: str
    source: str
    headline: str
    buyer: str
    target: str
    deal_value_m: Optional[float]
    value_range: str
    buyer_type: str
    sector: str
    technology_focus: str
    geography: str
    strategic_rationale: str = ""
    link: str = ""
    confidence_score: float = 1.0
    

class MATrackerConfig:
    """Configuration manager for the M&A tracker"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self.get_default_config()
    
    @staticmethod
    def get_default_config() -> Dict:
        """Return default configuration"""
        return {
            "deal_filters": {
                "turnover_range_millions": {"min": 5, "max": 50},
                "include_undisclosed": True,
                "days_lookback": 7
            },
            "output": {
                "format": "excel",
                "filename_pattern": "MA_Tracker_{date}.xlsx",
                "location": "/mnt/user-data/outputs"
            }
        }


class DealExtractor:
    """Extract and classify deal information from text"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.pe_indicators = config.get('buyer_classification', {}).get('private_equity_indicators', [])
        self.sectors = config.get('deal_filters', {}).get('sectors', [])
        
    def extract_deal(self, title: str, description: str, source: str, pub_date: datetime) -> Optional[Deal]:
        """Extract deal information from article"""
        text = f"{title} {description}"
        
        # Check if it's a relevant M&A deal
        if not self.is_ma_deal(text):
            return None
            
        # Extract components
        buyer, target = self.extract_companies(text)
        if not buyer or not target:
            return None
            
        deal_value = self.extract_value(text)
        value_range = self.categorize_value(deal_value)
        
        # Check if in target range
        min_val = self.config['deal_filters']['turnover_range_millions']['min']
        max_val = self.config['deal_filters']['turnover_range_millions']['max']
        
        if deal_value and not (min_val <= deal_value <= max_val):
            if not self.config['deal_filters'].get('include_undisclosed', True):
                return None
                
        return Deal(
            date=pub_date.strftime('%Y-%m-%d'),
            source=source,
            headline=title[:200],
            buyer=buyer,
            target=target,
            deal_value_m=deal_value,
            value_range=value_range,
            buyer_type=self.classify_buyer(text),
            sector=self.extract_sector(text),
            technology_focus=self.extract_technology(text),
            geography=self.extract_geography(text),
            strategic_rationale=self.extract_rationale(text),
            link="",
            confidence_score=self.calculate_confidence(text)
        )
    
    def is_ma_deal(self, text: str) -> bool:
        """Check if text describes an M&A deal"""
        deal_keywords = ['acqui', 'merger', 'buyout', 'purchase', 'deal', 'transaction']
        excluded = self.config['deal_filters'].get('excluded_keywords', [])
        
        text_lower = text.lower()
        has_deal = any(kw in text_lower for kw in deal_keywords)
        has_excluded = any(kw in text_lower for kw in excluded)
        
        return has_deal and not has_excluded
    
    def extract_companies(self, text: str) -> tuple:
        """Extract buyer and target company names - improved version"""
        import re
        
        patterns = [
            # "acquisition of TARGET by BUYER"
            (r'[Aa]cquisition\s+of\s+([A-Z][A-Za-z\s&]+?)\s+by\s+([A-Z][A-Za-z\s&]+)', True),
            # "BUYER acquires/buys TARGET"
            (r'([A-Z][A-Za-z\s&]+?)\s+(?:acquires?|buys?)\s+([A-Z][A-Za-z\s&]+)', False),
            # "BUYER to acquire/buy TARGET"  
            (r'([A-Z][A-Za-z\s&]+?)\s+to\s+(?:acquire|buy)\s+([A-Z][A-Za-z\s&]+)', False),
            # "BUYER merges with TARGET"
            (r'([A-Z][A-Za-z\s&]+?)\s+merges?\s+with\s+([A-Z][A-Za-z\s&]+)', False),
        ]
        
        def clean_name(name):
            if not name:
                return name
            # Remove "to" suffix from buyer names
            if name.endswith(' to'):
                name = name[:-3]
            # Remove trailing stop words
            stop_words = ['for', 'from', 'in', 'to', 'at', 'worth', 'expanding', 
                         'announced', 'completed', 'finalized', 'deal']
            words = name.split()
            company_suffixes = {'Inc', 'Ltd', 'LLC', 'Corp', 'Corporation', 'Limited', 'Co', 'plc', 'PLC'}
            while words and words[-1].lower() in stop_words and words[-1] not in company_suffixes:
                words.pop()
            return ' '.join(words)
        
        for pattern, reversed_order in patterns:
            match = re.search(pattern, text)
            if match:
                if reversed_order:
                    buyer = clean_name(match.group(2).strip())
                    target = clean_name(match.group(1).strip())
                else:
                    buyer = clean_name(match.group(1).strip())
                    target = clean_name(match.group(2).strip())
                if buyer and target:
                    return buyer, target
        
        return None, None
    
    def extract_value(self, text: str) -> Optional[float]:
        """Extract deal value from text"""
        import re
        patterns = [
            r'[$£€]\s*(\d+(?:\.\d+)?)\s*(?:m|million)',
            r'(\d+(?:\.\d+)?)\s*million',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None
    
    def categorize_value(self, value: Optional[float]) -> str:
        """Categorize deal value into ranges"""
        if value is None:
            return 'Undisclosed'
        elif value < 5:
            return '<£5m'
        elif value <= 10:
            return '£5-10m'
        elif value <= 25:
            return '£10-25m'
        elif value <= 50:
            return '£25-50m'
        else:
            return '>£50m'
    
    def classify_buyer(self, text: str) -> str:
        """Classify buyer type"""
        text_lower = text.lower()
        if any(ind in text_lower for ind in self.pe_indicators):
            return 'Private Equity'
        return 'Strategic'
    
    def extract_sector(self, text: str) -> str:
        """Extract primary sector"""
        text_lower = text.lower()
        for sector in self.sectors:
            if sector.lower() in text_lower:
                return sector
        return 'General Tech Services'
    
    def extract_technology(self, text: str) -> str:
        """Extract technology keywords"""
        tech_keywords = self.config.get('technology_keywords', {}).get('primary', [])
        text_lower = text.lower()
        found = [tech for tech in tech_keywords if tech in text_lower]
        return ', '.join(found[:3]) if found else 'General'
    
    def extract_geography(self, text: str) -> str:
        """Extract geographic location"""
        geo_mapping = self.config.get('geographic_mapping', {})
        text_lower = text.lower()
        
        for region, keywords in geo_mapping.items():
            if any(kw in text_lower for kw in keywords):
                return region
        return 'Unknown'
    
    def extract_rationale(self, text: str) -> str:
        """Extract strategic rationale if mentioned"""
        import re
        patterns = [
            r'(?:to|will|would)\s+([^.]{20,100})',
            r'(?:strategic|rationale|reason)[^.]{0,200}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)[:200]
        return ""
    
    def calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for the extraction"""
        score = 1.0
        # Reduce confidence for various factors
        if 'undisclosed' in text.lower():
            score *= 0.9
        if 'rumor' in text.lower() or 'report' in text.lower():
            score *= 0.8
        return score


class FeedProcessor:
    """Process RSS feeds to extract deals"""
    
    def __init__(self, config: Dict, extractor: DealExtractor):
        self.config = config
        self.extractor = extractor
        self.deals = []
        
    def process_opml(self, opml_path: str) -> List[Deal]:
        """Process all feeds in OPML file"""
        feeds = self.parse_opml(opml_path)
        
        for feed_info in feeds:
            logger.info(f"Processing: {feed_info['title']}")
            self.process_feed(feed_info)
            
        return self.deals
    
    def parse_opml(self, opml_path: str) -> List[Dict]:
        """Parse OPML file to extract feed URLs"""
        feeds = []
        try:
            tree = ET.parse(opml_path)
            root = tree.getroot()
            
            for outline in root.findall('.//outline[@type="rss"]'):
                feed_info = {
                    'title': outline.get('title', ''),
                    'url': outline.get('xmlUrl', '')
                }
                if feed_info['url']:
                    feeds.append(feed_info)
                    
            logger.info(f"Found {len(feeds)} RSS feeds")
        except Exception as e:
            logger.error(f"Error parsing OPML: {e}")
            
        return feeds
    
    def process_feed(self, feed_info: Dict):
        """Process a single RSS feed"""
        try:
            feed = feedparser.parse(feed_info['url'])
            lookback_days = self.config['deal_filters']['days_lookback']
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            
            for entry in feed.entries[:20]:  # Limit entries
                pub_date = self.get_pub_date(entry)
                
                if pub_date < cutoff_date:
                    continue
                    
                title = entry.get('title', '')
                description = entry.get('description', '') or entry.get('summary', '')
                
                deal = self.extractor.extract_deal(
                    title, description, feed_info['title'], pub_date
                )
                
                if deal:
                    deal.link = entry.get('link', '')
                    self.deals.append(deal)
                    logger.info(f"Found deal: {deal.buyer} → {deal.target}")
                    
        except Exception as e:
            logger.error(f"Error processing feed {feed_info['title']}: {e}")
    
    @staticmethod
    def get_pub_date(entry) -> datetime:
        """Extract publication date from feed entry"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6])
        return datetime.now()


class ReportGenerator:
    """Generate Excel reports from deals"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    def generate(self, deals: List[Deal], output_path: Optional[str] = None) -> str:
        """Generate Excel report from deals"""
        if not deals:
            logger.warning("No deals to report")
            return None
            
        # Convert deals to DataFrame
        df = pd.DataFrame([asdict(d) for d in deals])
        df = df.sort_values('date', ascending=False)
        
        # Calculate metrics
        metrics = self.calculate_metrics(df)
        
        # Determine output path
        if not output_path:
            date_str = datetime.now().strftime('%Y%m%d')
            filename = self.config['output']['filename_pattern'].replace('{date}', date_str)
            output_path = Path(self.config['output']['location']) / filename
            
        # Create Excel with multiple sheets
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main tracker
            df.to_excel(writer, sheet_name='Deal Tracker', index=False)
            
            # Executive summary
            summary_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
            summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
            
            # Sector analysis
            if 'sector' in df.columns:
                sector_analysis = df.groupby('sector').agg({
                    'target': 'count',
                    'deal_value_m': 'mean'
                }).round(1)
                sector_analysis.to_excel(writer, sheet_name='Sector Analysis')
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if cell.value and len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                    
        logger.info(f"Report saved to: {output_path}")
        return str(output_path)
    
    def calculate_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate key metrics from deals"""
        return {
            'Total Deals': len(df),
            'Date Range': f"{df['date'].min()} to {df['date'].max()}",
            'Avg Deal Value': f"${df['deal_value_m'].mean():.1f}M" if df['deal_value_m'].notna().any() else 'N/A',
            'Most Active Buyer Type': df['buyer_type'].mode().iloc[0] if len(df) > 0 else 'N/A',
            'Top Sector': df['sector'].value_counts().index[0] if len(df) > 0 else 'N/A',
            'Geographic Focus': df['geography'].value_counts().index[0] if len(df) > 0 else 'N/A'
        }


class MATracker:
    """Main M&A Tracker class"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_manager = MATrackerConfig(config_path)
        self.config = self.config_manager.config
        self.extractor = DealExtractor(self.config)
        self.processor = FeedProcessor(self.config, self.extractor)
        self.reporter = ReportGenerator(self.config)
        
    def run(self, opml_path: str, output_path: Optional[str] = None) -> str:
        """Run the complete tracking process"""
        logger.info("Starting M&A Tracker")
        
        # Process feeds
        deals = self.processor.process_opml(opml_path)
        
        # Generate report
        if deals:
            report_path = self.reporter.generate(deals, output_path)
            logger.info(f"Tracking complete. Found {len(deals)} deals.")
            return report_path
        else:
            logger.warning("No deals found in the specified period")
            return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='M&A Deal Tracker for Consulting & Tech Services')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--opml', default='data/rss_feeds.opml', help='Path to OPML file')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--days', type=int, help='Days to look back')
    parser.add_argument('--sector', help='Filter by sector')
    parser.add_argument('--disclosed-only', action='store_true', help='Only include deals with disclosed values')
    
    args = parser.parse_args()
    
    # Initialize tracker
    tracker = MATracker(args.config)
    
    # Override config with command line args
    if args.days:
        tracker.config['deal_filters']['days_lookback'] = args.days
    if args.sector:
        tracker.config['deal_filters']['sectors'] = [args.sector]
    if args.disclosed_only:
        tracker.config['deal_filters']['include_undisclosed'] = False
    
    # Run tracker
    report_path = tracker.run(args.opml, args.output)
    
    if report_path:
        print(f"\n✅ M&A Tracker complete!")
        print(f"📊 Report saved to: {report_path}")
    else:
        print("\n⚠️ No deals found matching criteria")
        

if __name__ == "__main__":
    main()
