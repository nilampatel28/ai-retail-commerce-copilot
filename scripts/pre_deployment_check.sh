#!/bin/bash

# Pre-Deployment Verification Script
# Run this before starting deployment to verify all prerequisites

echo "🔍 RetailBrain Copilot - Pre-Deployment Check"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $2 - Missing: $1"
        ((CHECKS_FAILED++))
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $2 - Missing: $1"
        ((CHECKS_FAILED++))
    fi
}

# Function to check command availability
check_command() {
    if command -v $1 &> /dev/null; then
        VERSION=$($1 --version 2>&1 | head -n 1)
        echo -e "${GREEN}✓${NC} $2 - $VERSION"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $2 - Not installed"
        ((CHECKS_FAILED++))
    fi
}

echo "📦 1. Checking Sample Data Files..."
check_file "data/products.csv" "Products data"
check_file "data/sales_history.csv" "Sales history data"
check_file "data/inventory_current.csv" "Inventory data"
check_file "data/pricing_history.csv" "Pricing history data"
check_file "data/alerts.csv" "Alerts data"
check_file "data/forecasts.csv" "Forecasts data"
check_file "data/recommendations.csv" "Recommendations data"
check_file "data/summary.json" "Data summary"
echo ""

echo "🔧 2. Checking Backend Code..."
check_file "backend/query_handler.py" "Lambda query handler"
check_file "backend/cdk_app.py" "CDK infrastructure code"
check_file "requirements.txt" "Python requirements"
echo ""

echo "🎨 3. Checking Frontend Files..."
check_file "frontend/package.json" "Frontend package.json"
check_dir "frontend" "Frontend directory"
echo ""

echo "📜 4. Checking Deployment Scripts..."
check_file "scripts/generate_sample_data.py" "Data generation script"
check_file "scripts/load_dynamodb.py" "DynamoDB loader script"
check_file "scripts/create_cognito_user.sh" "Cognito user creation script"
check_file "scripts/test_api.py" "API test script"
echo ""

echo "📚 5. Checking Documentation..."
check_file "README.md" "README"
check_file "QUICK-START.md" "Quick start guide"
check_file "DEPLOYMENT-GUIDE.md" "Deployment guide"
check_file "WINNING-STRATEGY.md" "Winning strategy"
check_file "PROJECT-SUMMARY.md" "Project summary"
check_file "STATUS.md" "Status document"
echo ""

echo "🛠️  6. Checking Required Tools..."
check_command "python3" "Python 3"
check_command "pip" "pip"
check_command "node" "Node.js"
check_command "npm" "npm"
check_command "git" "Git"
echo ""

echo "🐍 7. Checking Python Virtual Environment..."
if [ -d "venv" ] || [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Python virtual environment exists"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Python virtual environment not found (optional)"
fi
echo ""

echo "📊 8. Checking Data Statistics..."
if [ -f "data/summary.json" ]; then
    PRODUCTS=$(grep -o '"total_products": [0-9]*' data/summary.json | grep -o '[0-9]*')
    SALES=$(grep -o '"total_sales": [0-9]*' data/summary.json | grep -o '[0-9]*')
    echo -e "${GREEN}✓${NC} Products: $PRODUCTS"
    echo -e "${GREEN}✓${NC} Sales transactions: $SALES"
    ((CHECKS_PASSED+=2))
fi
echo ""

echo "=============================================="
echo "📊 Summary:"
echo -e "   ${GREEN}Passed: $CHECKS_PASSED${NC}"
echo -e "   ${RED}Failed: $CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! You're ready to deploy.${NC}"
    echo ""
    echo "Next steps when AWS credits arrive:"
    echo "1. Apply AWS credits to your account"
    echo "2. Configure AWS CLI: aws configure"
    echo "3. Enable Bedrock access in AWS Console"
    echo "4. Follow QUICK-START.md step-by-step"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Please fix the issues above.${NC}"
    echo ""
    exit 1
fi
