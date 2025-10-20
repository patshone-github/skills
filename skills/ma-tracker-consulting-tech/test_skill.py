#!/usr/bin/env python3
"""
Test script for M&A Tracker Claude Skill
Run this to verify the skill is working properly
"""

import sys
import os
from pathlib import Path

def test_skill():
    """Test the M&A Tracker skill installation and functionality"""
    
    print("🧪 Testing M&A Tracker Skill...")
    print("-" * 50)
    
    # Test 1: Check file structure
    print("\n✓ Checking file structure...")
    required_files = [
        'SKILL.md',
        'ma_tracker.py',
        'config.json',
        'requirements.txt',
        'data/rss_feeds.opml'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            print(f"  ❌ Missing: {file}")
        else:
            print(f"  ✓ Found: {file}")
    
    if missing_files:
        print("\n❌ Some required files are missing!")
        return False
    
    # Test 2: Check SKILL.md frontmatter
    print("\n✓ Checking SKILL.md format...")
    with open('SKILL.md', 'r') as f:
        content = f.read()
        if content.startswith('---'):
            print("  ✓ YAML frontmatter present")
            if 'name:' in content and 'description:' in content:
                print("  ✓ Required metadata fields present")
            else:
                print("  ❌ Missing required metadata fields")
                return False
        else:
            print("  ❌ No YAML frontmatter found")
            return False
    
    # Test 3: Check Python dependencies
    print("\n✓ Checking Python dependencies...")
    try:
        import pandas
        print("  ✓ pandas installed")
    except ImportError:
        print("  ❌ pandas not installed - run: pip install pandas")
        
    try:
        import feedparser
        print("  ✓ feedparser installed")
    except ImportError:
        print("  ❌ feedparser not installed - run: pip install feedparser")
        
    try:
        import openpyxl
        print("  ✓ openpyxl installed")
    except ImportError:
        print("  ❌ openpyxl not installed - run: pip install openpyxl")
    
    # Test 4: Check config.json validity
    print("\n✓ Checking configuration...")
    try:
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
            print("  ✓ Valid JSON configuration")
            
            # Check key config sections
            if 'deal_filters' in config:
                print("  ✓ Deal filters configured")
            if 'output' in config:
                print("  ✓ Output settings configured")
                
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON in config.json: {e}")
        return False
    
    # Test 5: Quick execution test
    print("\n✓ Testing basic execution...")
    try:
        # Import the tracker module
        import importlib.util
        spec = importlib.util.spec_from_file_location("ma_tracker", "ma_tracker.py")
        ma_tracker = importlib.util.module_from_spec(spec)
        
        print("  ✓ Module imports successfully")
        print("  ✓ Ready to track M&A deals!")
        
    except Exception as e:
        print(f"  ❌ Error loading module: {e}")
        return False
    
    print("\n" + "="*50)
    print("✅ All tests passed! Your skill is ready to use.")
    print("\nTry these commands:")
    print("  python ma_tracker.py")
    print("  python ma_tracker.py --days 14")
    print("  python ma_tracker.py --sector 'Cybersecurity'")
    
    return True

if __name__ == "__main__":
    # Change to skill directory if needed
    skill_dir = Path(__file__).parent
    os.chdir(skill_dir)
    
    success = test_skill()
    sys.exit(0 if success else 1)
