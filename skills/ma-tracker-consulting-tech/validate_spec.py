#!/usr/bin/env python3
"""
Agent Skills Spec Validator
Validates a skill folder against the official Agent Skills Spec v1.0
"""

import os
import re
import yaml
from pathlib import Path

class SkillValidator:
    def __init__(self, skill_path="."):
        self.skill_path = Path(skill_path).resolve()
        self.errors = []
        self.warnings = []
        self.info = []
        
    def validate(self):
        """Run all validation checks"""
        print("🔍 Validating against Agent Skills Spec v1.0")
        print("=" * 50)
        
        # Check 1: SKILL.md exists
        if not self.check_skill_md_exists():
            return False
            
        # Check 2: YAML frontmatter
        if not self.check_yaml_frontmatter():
            return False
            
        # Check 3: Folder name matches
        self.check_folder_name_match()
        
        # Print results
        self.print_results()
        
        return len(self.errors) == 0
        
    def check_skill_md_exists(self):
        """Check if SKILL.md exists"""
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            self.info.append("✓ SKILL.md file exists")
            return True
        else:
            self.errors.append("✗ SKILL.md file not found")
            return False
            
    def check_yaml_frontmatter(self):
        """Check YAML frontmatter compliance"""
        skill_md = self.skill_path / "SKILL.md"
        
        with open(skill_md, 'r') as f:
            content = f.read()
            
        # Check if starts with ---
        if not content.startswith('---'):
            self.errors.append("✗ SKILL.md must start with YAML frontmatter (---)")
            return False
            
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            self.errors.append("✗ Invalid YAML frontmatter format")
            return False
            
        try:
            frontmatter = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            self.errors.append(f"✗ Invalid YAML: {e}")
            return False
            
        # Check required fields
        if 'name' not in frontmatter:
            self.errors.append("✗ Missing required field: 'name'")
        else:
            name = frontmatter['name']
            # Validate name format (lowercase alphanumeric + hyphen)
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(f"✗ 'name' must be lowercase alphanumeric + hyphen only: '{name}'")
            else:
                self.info.append(f"✓ name: '{name}' (valid format)")
                
        if 'description' not in frontmatter:
            self.errors.append("✗ Missing required field: 'description'")
        else:
            self.info.append(f"✓ description: present ({len(frontmatter['description'])} chars)")
            
        # Check for non-spec fields
        valid_fields = {'name', 'description', 'license', 'allowed-tools', 'metadata'}
        extra_fields = set(frontmatter.keys()) - valid_fields
        
        if extra_fields:
            self.warnings.append(f"⚠ Non-spec fields found: {extra_fields}")
            self.warnings.append("  Consider moving to 'metadata' map")
            
        # Check optional fields
        if 'license' in frontmatter:
            self.info.append(f"  license: {frontmatter['license']}")
        if 'allowed-tools' in frontmatter:
            self.info.append(f"  allowed-tools: {frontmatter['allowed-tools']}")
        if 'metadata' in frontmatter:
            self.info.append(f"  metadata: {list(frontmatter['metadata'].keys())}")
            
        return len([e for e in self.errors if e.startswith("✗")]) == 0
        
    def check_folder_name_match(self):
        """Check if folder name matches the name in SKILL.md"""
        folder_name = self.skill_path.absolute().name
        
        skill_md = self.skill_path / "SKILL.md"
        with open(skill_md, 'r') as f:
            content = f.read()
            
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                if 'name' in frontmatter:
                    skill_name = frontmatter['name']
                    if folder_name == skill_name:
                        self.info.append(f"✓ Folder name matches skill name: '{folder_name}'")
                    else:
                        self.errors.append(f"✗ Folder name '{folder_name}' doesn't match skill name '{skill_name}'")
            except:
                pass
                
    def print_results(self):
        """Print validation results"""
        print("\n📋 VALIDATION RESULTS:")
        print("-" * 40)
        
        if self.info:
            print("\n✅ Compliant:")
            for msg in self.info:
                print(f"  {msg}")
                
        if self.warnings:
            print("\n⚠️  Warnings:")
            for msg in self.warnings:
                print(f"  {msg}")
                
        if self.errors:
            print("\n❌ Errors (must fix):")
            for msg in self.errors:
                print(f"  {msg}")
                
        print("\n" + "=" * 50)
        if not self.errors:
            print("✅ SKILL IS COMPLIANT WITH AGENT SKILLS SPEC v1.0")
        else:
            print(f"❌ {len(self.errors)} ERROR(S) FOUND - FIX REQUIRED")
            

if __name__ == "__main__":
    validator = SkillValidator()
    validator.validate()
