#!/bin/bash

# Claude Skills Installation Script
# Easily install skills from the repository to your Claude environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default paths
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${REPO_DIR}/skills"
DEFAULT_INSTALL_PATH="/mnt/skills/user"
CUSTOM_INSTALL_PATH=""

# Function to print colored output
print_color() {
    printf "${2}${1}${NC}\n"
}

# Function to print header
print_header() {
    echo ""
    print_color "=====================================" "${BLUE}"
    print_color "  Claude Skills Installer v1.0" "${BLUE}"
    print_color "=====================================" "${BLUE}"
    echo ""
}

# Function to check if skill exists
skill_exists() {
    local skill_name=$1
    if [ -d "${SKILLS_DIR}/${skill_name}" ]; then
        return 0
    else
        return 1
    fi
}

# Function to install Python dependencies
install_dependencies() {
    local skill_path=$1
    local requirements_file="${skill_path}/requirements.txt"
    
    if [ -f "${requirements_file}" ]; then
        print_color "Installing Python dependencies..." "${YELLOW}"
        pip install -r "${requirements_file}" --quiet || {
            print_color "Warning: Some dependencies may not have installed correctly" "${YELLOW}"
            print_color "Please manually run: pip install -r ${requirements_file}" "${YELLOW}"
        }
        print_color "✓ Dependencies installed" "${GREEN}"
    fi
}

# Function to install a single skill
install_skill() {
    local skill_name=$1
    local install_path=${CUSTOM_INSTALL_PATH:-$DEFAULT_INSTALL_PATH}
    
    if ! skill_exists "$skill_name"; then
        print_color "✗ Skill '${skill_name}' not found in repository" "${RED}"
        return 1
    fi
    
    print_color "Installing skill: ${skill_name}" "${BLUE}"
    
    # Create installation directory if it doesn't exist
    local target_dir="${install_path}/${skill_name}"
    
    # Check if skill is already installed
    if [ -d "${target_dir}" ]; then
        print_color "⚠ Skill already exists at ${target_dir}" "${YELLOW}"
        read -p "Overwrite? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_color "Skipping ${skill_name}" "${YELLOW}"
            return 0
        fi
        rm -rf "${target_dir}"
    fi
    
    # Copy skill files
    print_color "Copying skill files..." "${YELLOW}"
    mkdir -p "${target_dir}"
    cp -r "${SKILLS_DIR}/${skill_name}"/* "${target_dir}/"
    
    print_color "✓ Skill files copied to ${target_dir}" "${GREEN}"
    
    # Install dependencies
    install_dependencies "${target_dir}"
    
    # Run test if available
    if [ -f "${target_dir}/test_skill.py" ]; then
        print_color "Running skill tests..." "${YELLOW}"
        cd "${target_dir}"
        python test_skill.py > /dev/null 2>&1 && {
            print_color "✓ Tests passed" "${GREEN}"
        } || {
            print_color "⚠ Some tests failed - skill may still work" "${YELLOW}"
        }
        cd - > /dev/null
    fi
    
    print_color "✅ Successfully installed: ${skill_name}" "${GREEN}"
    echo ""
}

# Function to list available skills
list_skills() {
    print_color "Available skills:" "${BLUE}"
    echo ""
    
    for skill_dir in "${SKILLS_DIR}"/*; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            
            # Try to read description from SKILL.md
            skill_md="${skill_dir}/SKILL.md"
            if [ -f "$skill_md" ]; then
                description=$(grep -m 1 "^description:" "$skill_md" 2>/dev/null | cut -d':' -f2- | xargs) || description="No description available"
            else
                description="No description available"
            fi
            
            printf "  ${GREEN}%-30s${NC} %s\n" "$skill_name" "$description"
        fi
    done
    echo ""
}

# Function to install all skills
install_all() {
    print_color "Installing all available skills..." "${BLUE}"
    echo ""
    
    local count=0
    local failed=0
    
    for skill_dir in "${SKILLS_DIR}"/*; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            install_skill "$skill_name"
            if [ $? -eq 0 ]; then
                ((count++))
            else
                ((failed++))
            fi
        fi
    done
    
    echo ""
    print_color "=====================================" "${BLUE}"
    print_color "Installation Summary:" "${BLUE}"
    print_color "  Installed: ${count} skills" "${GREEN}"
    if [ $failed -gt 0 ]; then
        print_color "  Failed: ${failed} skills" "${RED}"
    fi
    print_color "=====================================" "${BLUE}"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] [SKILL_NAME]

Install Claude skills from the repository to your local environment.

OPTIONS:
    -h, --help              Show this help message
    -l, --list              List all available skills
    -a, --all               Install all available skills
    -p, --path PATH         Custom installation path (default: /mnt/skills/user)
    -t, --test              Test installation without copying files

EXAMPLES:
    $0 ma-tracker-consulting-tech     Install the M&A tracker skill
    $0 --all                          Install all skills
    $0 --list                         List available skills
    $0 -p ~/my-skills skill-name      Install to custom path

SKILL LOCATIONS:
    Default: ${DEFAULT_INSTALL_PATH}
    Custom:  Set with --path option

EOF
}

# Parse command line arguments
INSTALL_ALL=false
LIST_ONLY=false
TEST_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -l|--list)
            LIST_ONLY=true
            shift
            ;;
        -a|--all)
            INSTALL_ALL=true
            shift
            ;;
        -p|--path)
            CUSTOM_INSTALL_PATH="$2"
            shift 2
            ;;
        -t|--test)
            TEST_MODE=true
            shift
            ;;
        -*)
            print_color "Unknown option: $1" "${RED}"
            show_usage
            exit 1
            ;;
        *)
            SKILL_NAME="$1"
            shift
            ;;
    esac
done

# Main execution
print_header

# Check if running in test mode
if [ "$TEST_MODE" = true ]; then
    print_color "Running in TEST MODE - no files will be copied" "${YELLOW}"
    echo ""
fi

# Handle different modes
if [ "$LIST_ONLY" = true ]; then
    list_skills
elif [ "$INSTALL_ALL" = true ]; then
    install_all
elif [ -n "$SKILL_NAME" ]; then
    install_skill "$SKILL_NAME"
else
    print_color "No skill specified. Use -h for help." "${YELLOW}"
    echo ""
    list_skills
    echo "To install a skill, run:"
    print_color "  $0 <skill-name>" "${GREEN}"
    echo ""
fi

# Check if custom path was used
if [ -n "$CUSTOM_INSTALL_PATH" ]; then
    print_color "Note: Skills installed to custom path: ${CUSTOM_INSTALL_PATH}" "${BLUE}"
    print_color "Make sure Claude has access to this directory." "${YELLOW}"
fi
