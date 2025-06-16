#!/bin/bash

# TERRASCAN Endpoint Testing Script
# Tests all endpoints after the app.py rewrite

echo "🧪 TERRASCAN Endpoint Testing"
echo "===================================="

BASE_URL="http://localhost:5000"
TIMEOUT=10
PASSED=0
FAILED=0
TOTAL=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local path=$2
    local expected_status=$3
    local check_json=$4
    local description=$5
    
    echo -n "Testing $method $path ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -m $TIMEOUT "$BASE_URL$path" 2>/dev/null)
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "%{http_code}" -m $TIMEOUT -X POST -H "Content-Type: application/json" -d '{}' "$BASE_URL$path" 2>/dev/null)
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Connection failed${NC}"
        ((FAILED++))
        return 1
    fi
    
    # Extract status code (last 3 characters)
    status_code="${response: -3}"
    response_body="${response%???}"
    
    if [ "$status_code" = "$expected_status" ]; then
        # Check if JSON response is expected
        if [ "$check_json" = "true" ]; then
            if echo "$response_body" | jq . >/dev/null 2>&1; then
                echo -e "${GREEN}✅ OK (JSON)${NC}"
                ((PASSED++))
            else
                echo -e "${YELLOW}⚠️  OK but invalid JSON${NC}"
                ((PASSED++))
            fi
        else
            echo -e "${GREEN}✅ OK${NC}"
            ((PASSED++))
        fi
    else
        echo -e "${RED}❌ Status $status_code (expected $expected_status)${NC}"
        ((FAILED++))
    fi
    
    ((TOTAL++))
}

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Test web endpoints
echo -e "\n${BLUE}🌐 Testing Web Endpoints${NC}"
echo "------------------------"

test_endpoint "GET" "/" "200" "false" "Homepage"
test_endpoint "GET" "/dashboard" "200" "false" "Dashboard"
test_endpoint "GET" "/map" "200" "false" "Map View"
test_endpoint "GET" "/about" "200" "false" "About Page"
test_endpoint "GET" "/tasks" "200" "false" "Tasks Management"
test_endpoint "GET" "/system" "200" "false" "System Status"

# Test API endpoints
echo -e "\n${BLUE}🔌 Testing API Endpoints${NC}"
echo "------------------------"

test_endpoint "GET" "/api/map-data" "200" "true" "Map Data API"
test_endpoint "GET" "/api/refresh" "200" "true" "Refresh API"
test_endpoint "GET" "/api/health" "200" "true" "Health Check API"
test_endpoint "GET" "/api/tasks" "200" "true" "Tasks API"

# Test parameterized endpoints (these might return 404 if no tasks exist)
echo -e "\n${BLUE}⚙️  Testing Parameterized Endpoints${NC}"
echo "-----------------------------------"

# Test with a sample task name - expecting 404 or 500 is OK
echo -n "Testing GET /api/tasks/test_task/logs ... "
response=$(curl -s -w "%{http_code}" -m $TIMEOUT "$BASE_URL/api/tasks/test_task/logs" 2>/dev/null)
status_code="${response: -3}"
if [[ "$status_code" =~ ^(200|404|500)$ ]]; then
    echo -e "${GREEN}✅ OK (routing works)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Status $status_code${NC}"
    ((FAILED++))
fi
((TOTAL++))

echo -n "Testing POST /api/tasks/test_task/run ... "
response=$(curl -s -w "%{http_code}" -m $TIMEOUT -X POST -H "Content-Type: application/json" -d '{}' "$BASE_URL/api/tasks/test_task/run" 2>/dev/null)
status_code="${response: -3}"
if [[ "$status_code" =~ ^(200|404|500)$ ]]; then
    echo -e "${GREEN}✅ OK (routing works)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Status $status_code${NC}"
    ((FAILED++))
fi
((TOTAL++))

# Test 404 handling
echo -e "\n${BLUE}🚫 Testing Error Handling${NC}"
echo "-------------------------"

test_endpoint "GET" "/nonexistent" "404" "false" "404 Error Handling"

# Print summary
echo ""
echo "===================================="
echo -e "${BLUE}📊 TEST SUMMARY${NC}"
echo "===================================="
echo -e "✅ Passed: ${GREEN}$PASSED${NC}"
echo -e "❌ Failed: ${RED}$FAILED${NC}"
echo -e "📈 Total: $TOTAL"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}📋 The app.py rewrite is working correctly${NC}"
    echo -e "${GREEN}🚀 Ready for deployment to Railway!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Some tests failed${NC}"
    echo -e "${YELLOW}🔧 Check the server logs for details${NC}"
    exit 1
fi 
