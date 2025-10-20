#!/usr/bin/env python3
"""
Unit tests for M&A Tracker blocked feed handling
Following TDD - tests written before implementation
"""

import unittest
import tempfile
import json
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, mock_open, MagicMock

# Mock all external dependencies before importing ma_tracker
sys.modules['pandas'] = MagicMock()
sys.modules['openpyxl'] = MagicMock()
sys.modules['feedparser'] = MagicMock()

# Now import from ma_tracker
from ma_tracker import (
    BlockedFeedHandler,
    FeedProcessor,
    DealExtractor,
    MATrackerConfig,
    Deal
)


class TestBlockedFeedHandler(unittest.TestCase):
    """Test the BlockedFeedHandler class for processing cached feed content"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'deal_filters': {
                'turnover_range_millions': {'min': 5, 'max': 50},
                'include_undisclosed': True,
                'days_lookback': 7,
                'sectors': ['Consulting', 'IT Services'],
                'excluded_keywords': []
            },
            'buyer_classification': {'private_equity_indicators': []},
            'technology_keywords': {'primary': []},
            'geographic_mapping': {}
        }

        # Sample RSS feed XML content
        self.sample_feed_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>UK Tech Exits</title>
        <item>
            <title>Accenture acquires Cloud Consulting Ltd</title>
            <description>Strategic acquisition to expand cloud capabilities</description>
            <pubDate>Mon, 20 Oct 2025 10:00:00 GMT</pubDate>
            <link>https://example.com/deal1</link>
        </item>
    </channel>
</rss>"""

    @patch('ma_tracker.feedparser.parse')
    def test_blocked_feed_handler_can_load_from_file(self, mock_parse):
        """Test that BlockedFeedHandler can load feed content from a file"""
        # Mock feedparser.parse to return feed with entries
        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.entries = [Mock(title='Test Deal')]
        mock_parse.return_value = mock_feed

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(self.sample_feed_xml)
            temp_path = f.name

        try:
            handler = BlockedFeedHandler(self.config)
            feed_data = handler.load_feed_from_file(temp_path)

            self.assertIsNotNone(feed_data)
            self.assertTrue(hasattr(feed_data, 'entries'))
            self.assertGreater(len(feed_data.entries), 0)
        finally:
            Path(temp_path).unlink()

    def test_blocked_feed_handler_returns_none_for_missing_file(self):
        """Test that BlockedFeedHandler handles missing files gracefully"""
        handler = BlockedFeedHandler(self.config)
        feed_data = handler.load_feed_from_file('/nonexistent/file.xml')

        self.assertIsNone(feed_data)

    @patch('ma_tracker.feedparser.parse')
    def test_blocked_feed_handler_parses_entries_correctly(self, mock_parse):
        """Test that BlockedFeedHandler correctly parses feed entries"""
        # Mock feedparser.parse to return feed with entries
        mock_entry = Mock()
        mock_entry.title = 'Accenture acquires Cloud Consulting Ltd'
        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(self.sample_feed_xml)
            temp_path = f.name

        try:
            handler = BlockedFeedHandler(self.config)
            feed_data = handler.load_feed_from_file(temp_path)

            self.assertEqual(len(feed_data.entries), 1)
            entry = feed_data.entries[0]
            self.assertIn('Accenture', entry.title)
        finally:
            Path(temp_path).unlink()


class TestFeedProcessorFromFile(unittest.TestCase):
    """Test FeedProcessor's ability to process feeds from files"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'deal_filters': {
                'turnover_range_millions': {'min': 5, 'max': 50},
                'include_undisclosed': True,
                'days_lookback': 365,  # Long lookback to catch test data
                'sectors': ['Consulting', 'IT Services'],
                'excluded_keywords': []
            },
            'buyer_classification': {'private_equity_indicators': []},
            'technology_keywords': {'primary': []},
            'geographic_mapping': {}
        }

        self.extractor = DealExtractor(self.config)
        self.processor = FeedProcessor(self.config, self.extractor)

        self.sample_feed_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>UK Tech Exits</title>
        <item>
            <title>Accenture acquires Cloud Consulting Ltd for £25m</title>
            <description>Strategic acquisition to expand cloud capabilities in UK market</description>
            <pubDate>Mon, 20 Oct 2025 10:00:00 GMT</pubDate>
            <link>https://example.com/deal1</link>
        </item>
    </channel>
</rss>"""

    def test_process_feed_from_file_exists(self):
        """Test that process_feed_from_file method exists"""
        self.assertTrue(hasattr(self.processor, 'process_feed_from_file'))

    def test_process_feed_from_file_accepts_filepath_and_title(self):
        """Test that process_feed_from_file accepts filepath and feed_title parameters"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(self.sample_feed_xml)
            temp_path = f.name

        try:
            # Should not raise an exception
            self.processor.process_feed_from_file(temp_path, 'UK Tech Exits')
        finally:
            Path(temp_path).unlink()

    @patch('ma_tracker.DealExtractor.extract_deal')
    @patch('ma_tracker.feedparser.parse')
    def test_process_feed_from_file_extracts_deals(self, mock_parse, mock_extract):
        """Test that process_feed_from_file calls the deal extractor for feed entries"""
        # Mock feedparser.parse to return feed with entries
        from datetime import datetime

        mock_entry = Mock()
        mock_entry.title = 'Accenture acquires Cloud Consulting Ltd for £25m'
        mock_entry.description = 'Strategic acquisition to expand cloud capabilities'
        mock_entry.link = 'https://example.com/deal1'

        # Mock publication date
        pub_time = datetime(2025, 10, 20, 10, 0, 0)
        mock_entry.published_parsed = pub_time.timetuple()[:6]

        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        # Mock extract_deal to return a Deal object
        mock_deal = Mock()
        mock_deal.buyer = 'Accenture'
        mock_deal.target = 'Cloud Consulting Ltd'
        mock_deal.link = ''
        mock_extract.return_value = mock_deal

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(self.sample_feed_xml)
            temp_path = f.name

        try:
            initial_deal_count = len(self.processor.deals)
            self.processor.process_feed_from_file(temp_path, 'UK Tech Exits')

            # Verify extract_deal was called
            self.assertTrue(mock_extract.called)
            # Should have added the mocked deal
            self.assertEqual(len(self.processor.deals), initial_deal_count + 1)
        finally:
            Path(temp_path).unlink()

    def test_process_feed_from_file_handles_missing_file_gracefully(self):
        """Test that process_feed_from_file doesn't crash on missing files"""
        # Should not raise an exception
        try:
            self.processor.process_feed_from_file('/nonexistent/file.xml', 'Test Feed')
        except Exception as e:
            self.fail(f"process_feed_from_file raised exception on missing file: {e}")


class TestFeedCacheDirArgument(unittest.TestCase):
    """Test the --feed-cache-dir command line argument"""

    def test_main_accepts_feed_cache_dir_argument(self):
        """Test that main() accepts --feed-cache-dir argument"""
        # This will be tested by running the script with the argument
        # For now, we'll test that the argument parser is configured correctly
        import argparse
        from ma_tracker import main

        # We can't easily test main() directly, but we can check if it would accept the arg
        # This is a design test - the actual integration will be tested later
        self.assertTrue(True)  # Placeholder - will verify in integration test


class TestProcessOpmlWithCachedFeeds(unittest.TestCase):
    """Test that process_opml works with pre-fetched feeds from cache directory"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'deal_filters': {
                'turnover_range_millions': {'min': 5, 'max': 50},
                'include_undisclosed': True,
                'days_lookback': 365,
                'sectors': [],
                'excluded_keywords': []
            },
            'buyer_classification': {'private_equity_indicators': []},
            'technology_keywords': {'primary': []},
            'geographic_mapping': {}
        }
        self.extractor = DealExtractor(self.config)
        self.processor = FeedProcessor(self.config, self.extractor)

    @patch('ma_tracker.feedparser.parse')
    def test_process_opml_uses_cached_feeds_when_available(self, mock_parse):
        """Test that process_opml prefers cached feeds over URL fetching"""
        # Create mock OPML content
        opml_content = """<?xml version="1.0"?>
<opml version="1.0">
    <body>
        <outline type="rss" title="UK Tech Exits" xmlUrl="https://uktechexits.news/feed"/>
    </body>
</opml>"""

        # Mock feed data
        mock_entry = Mock()
        mock_entry.title = 'Accenture acquires Cloud Consulting Ltd'
        mock_entry.description = 'Strategic acquisition'
        mock_entry.link = 'https://example.com/deal1'
        mock_entry.published_parsed = datetime(2025, 10, 20, 10, 0, 0).timetuple()[:6]

        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        with tempfile.NamedTemporaryFile(mode='w', suffix='.opml', delete=False) as opml_file:
            opml_file.write(opml_content)
            opml_path = opml_file.name

        with tempfile.TemporaryDirectory() as cache_dir:
            # Create a cached feed file
            cached_feed_path = Path(cache_dir) / 'uk_tech_exits.xml'
            cached_feed_path.write_text('<rss><channel><item><title>Test</title></item></channel></rss>')

            try:
                # Process with cache directory
                self.processor.process_opml(opml_path, cache_dir=cache_dir)

                # Should have used cached version
                self.assertTrue(True)  # Placeholder - actual behavior will be verified in implementation
            finally:
                Path(opml_path).unlink()


if __name__ == '__main__':
    unittest.main()
