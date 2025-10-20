#!/usr/bin/env python3
"""
Helper script for handling blocked RSS feeds in M&A Tracker

This script processes feed content retrieved via Claude's WebFetch tool
and saves it to standardized locations for processing by ma_tracker.py

Usage:
    # In Claude Code, after fetching a blocked feed with WebFetch:
    python fetch_blocked_feeds.py --feed-name "uktechexits" --content-file /tmp/feed.xml

    # Or provide content directly via stdin:
    echo "<rss>...</rss>" | python fetch_blocked_feeds.py --feed-name "uktechexits"
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import tempfile


class BlockedFeedCache:
    """Manages caching of blocked RSS feeds"""

    def __init__(self, cache_dir: str = None):
        """
        Initialize the blocked feed cache.

        Args:
            cache_dir: Directory to store cached feeds. Defaults to /tmp/ma_tracker_feeds
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(tempfile.gettempdir()) / "ma_tracker_feeds"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "feed_metadata.json"

    def save_feed(self, feed_name: str, content: str) -> dict:
        """
        Save feed content to cache directory.

        Args:
            feed_name: Name identifier for the feed (e.g., "uktechexits")
            content: RSS/XML feed content

        Returns:
            dict with metadata about the saved feed
        """
        # Sanitize feed name for filename
        safe_name = "".join(c for c in feed_name if c.isalnum() or c in ('-', '_')).lower()

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{timestamp}.xml"
        filepath = self.cache_dir / filename

        # Write content to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Update metadata
        metadata = {
            'feed_name': feed_name,
            'safe_name': safe_name,
            'filepath': str(filepath),
            'filename': filename,
            'cached_at': timestamp,
            'size_bytes': len(content.encode('utf-8'))
        }

        self._update_metadata(safe_name, metadata)

        return metadata

    def _update_metadata(self, safe_name: str, metadata: dict):
        """Update the metadata file with information about cached feeds"""
        # Load existing metadata
        all_metadata = {}
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                all_metadata = json.load(f)

        # Update with new entry
        all_metadata[safe_name] = metadata

        # Save updated metadata
        with open(self.metadata_file, 'w') as f:
            json.dump(all_metadata, f, indent=2)

    def get_latest_feed_path(self, feed_name: str) -> str:
        """
        Get the filepath of the most recently cached version of a feed.

        Args:
            feed_name: Name identifier for the feed

        Returns:
            Path to cached feed file, or None if not found
        """
        if not self.metadata_file.exists():
            return None

        with open(self.metadata_file, 'r') as f:
            all_metadata = json.load(f)

        safe_name = "".join(c for c in feed_name if c.isalnum() or c in ('-', '_')).lower()

        if safe_name in all_metadata:
            return all_metadata[safe_name]['filepath']

        return None

    def list_cached_feeds(self) -> list:
        """
        List all cached feeds.

        Returns:
            List of metadata dicts for all cached feeds
        """
        if not self.metadata_file.exists():
            return []

        with open(self.metadata_file, 'r') as f:
            all_metadata = json.load(f)

        return list(all_metadata.values())


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description='Cache blocked RSS feeds for M&A Tracker processing'
    )
    parser.add_argument(
        '--feed-name',
        required=True,
        help='Name identifier for the feed (e.g., "uktechexits")'
    )
    parser.add_argument(
        '--content-file',
        help='Path to file containing feed content (or use stdin)'
    )
    parser.add_argument(
        '--cache-dir',
        help='Directory to cache feeds (default: /tmp/ma_tracker_feeds)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all cached feeds and exit'
    )

    args = parser.parse_args()

    # Initialize cache
    cache = BlockedFeedCache(args.cache_dir)

    # List cached feeds if requested
    if args.list:
        cached_feeds = cache.list_cached_feeds()
        if not cached_feeds:
            print("No cached feeds found.")
        else:
            print(f"Cached feeds in {cache.cache_dir}:")
            for feed in cached_feeds:
                print(f"  - {feed['feed_name']} ({feed['filename']})")
                print(f"    Cached at: {feed['cached_at']}")
                print(f"    Size: {feed['size_bytes']} bytes")
                print(f"    Path: {feed['filepath']}")
        return

    # Read feed content
    if args.content_file:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # Read from stdin
        content = sys.stdin.read()

    if not content.strip():
        print("Error: No feed content provided", file=sys.stderr)
        sys.exit(1)

    # Save feed
    metadata = cache.save_feed(args.feed_name, content)

    print(f"✓ Feed cached successfully!")
    print(f"  Feed name: {metadata['feed_name']}")
    print(f"  Saved to: {metadata['filepath']}")
    print(f"  Size: {metadata['size_bytes']} bytes")
    print(f"\nTo process this feed with ma_tracker.py:")
    print(f"  python ma_tracker.py --feed-cache-dir {cache.cache_dir}")


if __name__ == '__main__':
    main()
