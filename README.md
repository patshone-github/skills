# Claude Skills Repository

A curated collection of skills for Claude AI, enabling specialized capabilities for business automation, data analysis, and workflow enhancement.

## 🚀 Quick Start

### Installing a Skill

1. **Browse Available Skills**: Check the [Skills Catalog](#available-skills) below or view `marketplace.json`
2. **Download the Skill**: Clone this repository or download individual skill folders
3. **Install in Claude**: 
   - Copy the skill folder to your Claude skills directory
   - Or use the installation script: `./install.sh <skill-name>`

### Using Skills with Claude

Simply reference the skill in your conversation:
```
"Use the M&A tracker skill to find consulting acquisitions from last week"
```

## 📦 Available Skills

| Skill | Description | Version | Category |
|-------|-------------|---------|----------|
| [ma-tracker-consulting-tech](./skills/ma-tracker-consulting-tech) | Track and analyze M&A deals in consulting and tech services (£5-50m) | 1.0.0 | Finance/Analytics |

## 🏗️ Repository Structure

```
skills/
├── README.md                    # This file
├── marketplace.json             # Skill catalog with metadata
├── install.sh                   # Installation helper script
├── skills/                      # Individual skill directories
│   └── ma-tracker-consulting-tech/
│       ├── SKILL.md            # Skill documentation
│       ├── *.py                # Implementation files
│       ├── config.json         # Configuration
│       └── requirements.txt    # Python dependencies
└── templates/                   # Skill templates for developers
```

## 💿 Installation Methods

### Method 1: Direct Download
```bash
# Clone the entire repository
git clone https://github.com/patshone-github/skills.git

# Or download a specific skill
wget https://github.com/patshone-github/skills/archive/main.zip
```

### Method 2: Using Installation Script
```bash
# Install a specific skill
./install.sh ma-tracker-consulting-tech

# Install all skills
./install.sh --all
```

### Method 3: Manual Installation
1. Download the skill folder
2. Place it in your Claude skills directory:
   - User skills: `/mnt/skills/user/<skill-name>/`
   - Or specify custom path in Claude

## 🔧 Configuration

Each skill includes a `config.json` file that can be customized:

```json
{
  "skill_name": "Skill Name",
  "version": "1.0.0",
  "settings": {
    // Skill-specific settings
  }
}
```

## 📋 Requirements

- Python 3.8+ for Python-based skills
- Dependencies listed in each skill's `requirements.txt`
- Claude AI with skills support enabled

## 🔧 Adding New Skills

To add a new skill:

1. Create a new folder in `skills/` with your skill name
2. Include required files: `SKILL.md`, implementation files, `config.json`, `requirements.txt`
3. Add skill metadata to `marketplace.json`
4. Test the skill thoroughly

### Skill Requirements
- Must include `SKILL.md` with proper YAML frontmatter
- Follow the Agent Skills Spec v1.0
- Include comprehensive documentation
- Add tests where applicable

## 📊 Skill Categories

- **Finance/Analytics**: Financial analysis, M&A tracking, market research
- **Productivity**: Task automation, document generation, workflow optimization
- **Data Processing**: ETL, data cleaning, analysis, visualization
- **Communication**: Email automation, report generation, notifications
- **Development**: Code generation, testing, deployment tools

## 🛟 Support

- **Issues**: [GitHub Issues](https://github.com/patshone-github/skills/issues)
- **Discussions**: [GitHub Discussions](https://github.com/patshone-github/skills/discussions)
- **Documentation**: Each skill includes detailed documentation in its `SKILL.md` file

## 📜 License

Skills in this repository are provided under various licenses. Check each skill's directory for specific license information.

## 🌟 Featured Skills

### M&A Tracker - Consulting & Tech Services
Track and analyze merger & acquisition activity in the consulting and technology services sectors with automated RSS feed monitoring and Excel report generation.

**Key Features:**
- 📰 Monitors 13+ industry RSS feeds
- 💰 Focuses on deals £5-50m
- 📊 Generates comprehensive Excel reports
- 🎯 Sector and technology analysis
- 🚨 Alert system for high-priority deals

[Learn More →](./skills/ma-tracker-consulting-tech/README.md)

---

## 🔄 Updates

- **v1.0.0** (2025-10-20): Initial release with M&A Tracker skill
- More skills coming soon!

## 🏷️ Tags

`claude-ai` `skills` `automation` `m&a-tracking` `consulting` `technology` `finance` `analytics` `productivity`
