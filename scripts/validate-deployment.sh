#!/bin/bash
# FastMCP Cloud Deployment Validation Script
# Validates server is ready for deployment

set -e

SERVER_DIR="${1:-.}"
ERRORS=0
WARNINGS=0
CHECKS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== FastMCP Cloud Deployment Validation ===${NC}\n"

# Check 1: Server file exists
echo -n "Checking for server file... "
CHECKS=$((CHECKS + 1))
if [ -f "$SERVER_DIR/server.py" ]; then
    echo -e "${GREEN}✓ Found server.py${NC}"
else
    echo -e "${RED}✗ server.py not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: Python syntax validation
if [ -f "$SERVER_DIR/server.py" ]; then
    echo -n "Validating Python syntax... "
    CHECKS=$((CHECKS + 1))
    if python3 -m py_compile "$SERVER_DIR/server.py" 2>/dev/null; then
        echo -e "${GREEN}✓ Python syntax valid${NC}"
    else
        echo -e "${RED}✗ Python syntax errors${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check 3: FastMCP dependency
echo -n "Checking FastMCP dependency... "
CHECKS=$((CHECKS + 1))
if [ -f "$SERVER_DIR/requirements.txt" ]; then
    if grep -q "fastmcp" "$SERVER_DIR/requirements.txt"; then
        echo -e "${GREEN}✓ FastMCP dependency declared${NC}"
    else
        echo -e "${RED}✗ FastMCP not in requirements.txt${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: Google Gen AI dependency
echo -n "Checking google-genai dependency... "
CHECKS=$((CHECKS + 1))
if [ -f "$SERVER_DIR/requirements.txt" ]; then
    if grep -q "google-genai" "$SERVER_DIR/requirements.txt"; then
        echo -e "${GREEN}✓ google-genai dependency declared${NC}"
    else
        echo -e "${RED}✗ google-genai not in requirements.txt${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check 5: fastmcp.json exists and is valid
echo -n "Checking fastmcp.json... "
CHECKS=$((CHECKS + 1))
if [ -f "$SERVER_DIR/fastmcp.json" ]; then
    if python3 -c "import json; json.load(open('$SERVER_DIR/fastmcp.json'))" 2>/dev/null; then
        echo -e "${GREEN}✓ fastmcp.json is valid JSON${NC}"
    else
        echo -e "${RED}✗ fastmcp.json has invalid JSON${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠ fastmcp.json not found (optional)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 6: Server entrypoint in fastmcp.json
if [ -f "$SERVER_DIR/fastmcp.json" ]; then
    echo -n "Checking server entrypoint... "
    CHECKS=$((CHECKS + 1))
    ENTRYPOINT=$(python3 -c "import json; data=json.load(open('$SERVER_DIR/fastmcp.json')); print(data.get('source', {}).get('entrypoint', 'mcp'))" 2>/dev/null)
    if [ "$ENTRYPOINT" = "mcp" ]; then
        echo -e "${GREEN}✓ Entrypoint set to 'mcp'${NC}"
    else
        echo -e "${YELLOW}⚠ Entrypoint is '$ENTRYPOINT' (expected 'mcp')${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Check 7: .env.example exists
echo -n "Checking .env.example... "
CHECKS=$((CHECKS + 1))
if [ -f "$SERVER_DIR/.env.example" ]; then
    echo -e "${GREEN}✓ .env.example exists${NC}"
else
    echo -e "${YELLOW}⚠ .env.example not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 8: Required environment variable documented
if [ -f "$SERVER_DIR/.env.example" ]; then
    echo -n "Checking GOOGLE_API_KEY documentation... "
    CHECKS=$((CHECKS + 1))
    if grep -q "GOOGLE_API_KEY" "$SERVER_DIR/.env.example"; then
        echo -e "${GREEN}✓ GOOGLE_API_KEY documented${NC}"
    else
        echo -e "${RED}✗ GOOGLE_API_KEY not documented in .env.example${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check 9: .gitignore excludes .env
echo -n "Checking .gitignore... "
CHECKS=$((CHECKS + 1))
if [ -f "$SERVER_DIR/.gitignore" ]; then
    if grep -q "^\.env$" "$SERVER_DIR/.gitignore" || grep -q "^\.env" "$SERVER_DIR/.gitignore"; then
        echo -e "${GREEN}✓ .env excluded from git${NC}"
    else
        echo -e "${YELLOW}⚠ .env might not be excluded from git${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠ .gitignore not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 10: No hardcoded API keys
echo -n "Scanning for hardcoded secrets... "
CHECKS=$((CHECKS + 1))
if [ -f "$SERVER_DIR/server.py" ]; then
    # Simple pattern matching for common API key formats
    if grep -E "(sk-[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9_-]{35})" "$SERVER_DIR/server.py" >/dev/null 2>&1; then
        echo -e "${RED}✗ Potential hardcoded API key detected${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓ No obvious hardcoded secrets${NC}"
    fi
fi

# Check 11: Git repository status
if [ -d "$SERVER_DIR/.git" ]; then
    echo -n "Checking git status... "
    CHECKS=$((CHECKS + 1))
    cd "$SERVER_DIR"
    if [ -z "$(git status --porcelain)" ]; then
        echo -e "${GREEN}✓ Working directory clean${NC}"
    else
        echo -e "${YELLOW}⚠ Uncommitted changes present${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    echo -n "Checking git remote... "
    CHECKS=$((CHECKS + 1))
    if git remote get-url origin >/dev/null 2>&1; then
        REMOTE_URL=$(git remote get-url origin)
        echo -e "${GREEN}✓ Git remote configured: $REMOTE_URL${NC}"
    else
        echo -e "${RED}✗ No git remote configured${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check 12: Python version
echo -n "Checking Python version... "
CHECKS=$((CHECKS + 1))
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
REQUIRED_VERSION="3.10"
if awk "BEGIN {exit !($PYTHON_VERSION >= $REQUIRED_VERSION)}"; then
    echo -e "${GREEN}✓ Python $PYTHON_VERSION (>= $REQUIRED_VERSION)${NC}"
else
    echo -e "${YELLOW}⚠ Python $PYTHON_VERSION (recommended >= $REQUIRED_VERSION)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo -e "${BLUE}=== Validation Summary ===${NC}"
echo -e "Total checks: $CHECKS"
echo -e "${GREEN}Passed: $((CHECKS - ERRORS - WARNINGS))${NC}"
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
fi
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}Errors: $ERRORS${NC}"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Server passed validation - ready for deployment${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Visit https://cloud.fastmcp.com"
    echo "2. Create new project with:"
    echo "   - Repository: vanman2024/content-image-generation-mcp"
    echo "   - Entrypoint: server.py:mcp"
    echo "   - Environment: GOOGLE_API_KEY=<your-key>"
    echo "3. Click Deploy"
    exit 0
else
    echo -e "${RED}✗ Validation failed - fix errors before deployment${NC}"
    exit 1
fi
