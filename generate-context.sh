#!/bin/bash
#
# Description:
# This script generates a comprehensive prompt for an LLM by concatenating key source
# files from the Telegram AI Bot project, including Python bot code, database schemas,
# configuration files, and project structure.
#
# Usage:
# ./generate-context.sh
#

# --- Configuration ---

# Get current date for the output filename (readable format)
DATE=$(date '+%Y-%m-%d_%H-%M-%S_%Z')

# Output filename with a timestamp
OUTPUT_FILE="telegram-bot-context-prompt-${DATE}.txt"

# --- Script Body ---

# Clean up any previous output file to start fresh
rm -f "$OUTPUT_FILE"

echo "🚀 Starting LLM prompt generation for the Telegram AI Bot project..."
echo "------------------------------------------------------------"
echo "Output will be saved to: $OUTPUT_FILE"
echo ""

# 1. Add a Preamble and Goal for the LLM
echo "Adding LLM preamble and goal..."
{
  echo "# Telegram AI Bot Project Context & Goal"
  echo ""
  echo "## Goal for the LLM"
  echo "You are an expert Python developer and AI bot architect with deep expertise in:"
  echo "- Telegram Bot API and python-telegram-bot library"
  echo "- AI/LLM integration (OpenAI/OpenRouter APIs)"
  echo "- Database design with Supabase/PostgreSQL"
  echo "- Modern Python development with UV package manager"
  echo "- Bot conversation design and user experience"
  echo ""
  echo "Your task is to analyze the complete context of this Telegram AI Bot project. The bot features:"
  echo "- Conversation persistence with Supabase"
  echo "- Real-time AI responses via WebSocket"
  echo "- Works in groups (mention to respond) and in DMs"
  echo "- Rate limiting per chat"
  echo ""
  echo "Please review the project structure, dependencies, source code, database schema, and configuration,"
  echo "then provide specific, actionable advice for improvement. Focus on:"
  echo "- Code quality and Python best practices"
  echo "- Bot conversation flow and UX"
  echo "- Database optimization and design"
  echo "- AI prompt engineering and response quality"
  echo "- Security and error handling"
  echo "- Performance and scalability"
  echo "- Deployment and production readiness"
  echo ""
  echo "---"
  echo ""
} >> "$OUTPUT_FILE"

# 2. Add the project's directory structure (cleaned up)
echo "Adding cleaned directory structure..."
echo "## Directory Structure" >> "$OUTPUT_FILE"
if command -v tree &> /dev/null; then
    echo "  -> Adding directory structure (tree -L 4)"
    # Exclude common noise from the tree view
    tree -L 4 -I "__pycache__|.venv|venv|.git|.pytest_cache|.ruff_cache|.mypy_cache|htmlcov|*.pyc|uv.lock" >> "$OUTPUT_FILE"
else
    echo "  -> WARNING: 'tree' command not found. Using ls -la instead."
    echo "NOTE: 'tree' command was not found. Directory listing:" >> "$OUTPUT_FILE"
    ls -la >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# 3. Add Core Project and Configuration Files
echo "Adding core project and configuration files..."
# Core files that provide project context
CORE_FILES=(
  "README.md"
  "pyproject.toml"
  "env.example"
  ".gitignore"
  "render.yaml"
  "requirements.txt"
  "$0" # This script itself
)

for file in "${CORE_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  -> Adding $file"
    echo "## FILE: $file" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  else
    echo "  -> WARNING: $file not found. Skipping."
  fi
done

# 4. Add all Python source files from project root (and src/ if present)
echo "Adding Python source files..."

# From root
find . -maxdepth 1 -type f -name "*.py" \
  | while read -r py_file; do
    echo "  -> Adding Python file: $py_file"
    echo "## FILE: $py_file" >> "$OUTPUT_FILE"
    cat "$py_file" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  done

# From src/bot if such layout exists
if [ -d "src/bot" ]; then
  echo "  -> Found src/bot layout; adding its Python files"
  find "src/bot" -type f -name "*.py" \
    -not -path "*/__pycache__/*" \
    | while read -r py_file; do
      echo "  -> Adding Python file: $py_file"
      echo "## FILE: $py_file" >> "$OUTPUT_FILE"
      cat "$py_file" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
      echo "---" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
    done
fi

# 5. Add test files
echo "Adding test files from 'tests/'..."
if [ -d "tests" ]; then
  find "tests" -type f -name "*.py" \
    -not -path "*/__pycache__/*" \
    | while read -r test_file; do
      echo "  -> Adding test file: $test_file"
      echo "## FILE: $test_file" >> "$OUTPUT_FILE"
      cat "$test_file" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
      echo "---" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
    done
else
  echo "  -> No tests directory found. Skipping."
fi

# 6. Add script files
echo "Adding script files from 'scripts/'..."
if [ -d "scripts" ]; then
  find "scripts" -type f \( -name "*.py" -o -name "*.sh" \) \
    | while read -r script_file; do
      echo "  -> Adding script file: $script_file"
      echo "## FILE: $script_file" >> "$OUTPUT_FILE"
      cat "$script_file" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
      echo "---" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
    done
else
  echo "  -> No scripts directory found. Skipping."
fi

# 7. Add database migration/schema files if present
echo "Adding database migration/schema files if present..."
DB_FILES=(
  "schema.sql"
  "database_schema.sql"
  "migrations.sql"
  "supabase_schema.sql"
)

for db_file in "${DB_FILES[@]}"; do
  if [ -f "$db_file" ]; then
    echo "  -> Adding database file: $db_file"
    echo "## FILE: $db_file" >> "$OUTPUT_FILE"
    cat "$db_file" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  fi
done

# 8. Add Docker files if present
echo "Adding Docker files if present..."
DOCKER_FILES=(
  "Dockerfile"
  "docker-compose.yml"
  "docker-compose.yaml"
  ".dockerignore"
)

for docker_file in "${DOCKER_FILES[@]}"; do
  if [ -f "$docker_file" ]; then
    echo "  -> Adding Docker file: $docker_file"
    echo "## FILE: $docker_file" >> "$OUTPUT_FILE"
    cat "$docker_file" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  fi
done

# --- Completion Summary ---

echo ""
echo "-------------------------------------"
echo "✅ Prompt generation complete!"
echo "Generated on: $(date '+%A, %B %d, %Y at %I:%M:%S %p %Z')"
echo ""
echo "This context file now includes:"
echo "  ✓ A clear goal and preamble for the LLM"
echo "  ✓ A cleaned project directory structure"
echo "  ✓ Core project files (README.md, pyproject.toml, env.example)"
echo "  ✓ Configuration files (.gitignore, render.yaml, requirements.txt)"
echo "  ✓ This generation script itself"
echo "  ✓ All Python source code from the project (*.py)"
echo "  ✓ Test files from the 'tests' directory (if present)"
echo "  ✓ Script files from the 'scripts' directory (if present)"
echo "  ✓ Database schema files (if present)"
echo "  ✓ Docker configuration files (if present)"
echo ""
echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "Total lines: $(wc -l < "$OUTPUT_FILE" | xargs)"
echo ""
echo "You can now use the content of '$OUTPUT_FILE' as a context prompt for your LLM."
echo "Perfect for getting comprehensive code reviews, architecture advice, or feature suggestions!"
echo ""
echo "💡 Tip: This is especially useful for:"
echo "   - Code reviews and optimization suggestions"
echo "   - Bot conversation flow improvements"
echo "   - Database schema optimization"
echo "   - AI prompt engineering enhancements"
echo "   - Production deployment planning"


