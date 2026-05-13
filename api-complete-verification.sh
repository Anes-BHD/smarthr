#!/bin/bash

# SmartHR Complete API Test Verification Script
# Tests all available API endpoints with authentication

BASE_URL="http://127.0.0.1:8002"
API_PREFIX="/api/v1"

echo "========================================="
echo "SmartHR Complete API Verification"
echo "========================================="
echo ""

# Step 1: Authenticate
echo "Step 1: Authenticating..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"employee@smarthr.com","password":"password"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')
USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.user.id')

if [ "$TOKEN" == "null" ]; then
  echo "✗ Authentication failed"
  exit 1
fi

echo "✓ Authentication successful"
echo ""

# Test endpoint function
test_endpoint() {
  local name=$1
  local method=${2:-GET}
  local endpoint=$3
  
  if [ "$method" == "GET" ]; then
    RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL$API_PREFIX$endpoint")
  else
    RESPONSE=$(curl -s -X "$method" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" "$BASE_URL$API_PREFIX$endpoint")
  fi
  
  COUNT=$(echo "$RESPONSE" | jq '.data | if type == "array" then length else 1 end' 2>/dev/null || echo "0")
  ERROR=$(echo "$RESPONSE" | jq -r '.message // .error // empty' 2>/dev/null)
  
  if [ ! -z "$ERROR" ] && [ "$ERROR" != "null" ]; then
    echo "✗ $name - Error: $ERROR"
  elif [ "$COUNT" -gt 0 ] || [ "$COUNT" == "0" ]; then
    echo "✓ $name - $COUNT items"
  else
    echo "? $name - Unable to determine status"
  fi
}

# Test all endpoints
echo "Step 2: Testing HR Module Endpoints"
echo "========================================="
test_endpoint "Employees" "GET" "/employees"
test_endpoint "Clients" "GET" "/clients"
test_endpoint "Departments" "GET" "/departments"
test_endpoint "Designations" "GET" "/designations"
test_endpoint "Users" "GET" "/users"
test_endpoint "Attendances" "GET" "/attendances"
test_endpoint "Payslips" "GET" "/payslips"
test_endpoint "Holidays" "GET" "/holidays"
test_endpoint "Tickets" "GET" "/tickets"
test_endpoint "Assets" "GET" "/assets"

echo ""
echo "Step 3: Testing Sales Module Endpoints"
echo "========================================="
test_endpoint "Invoices" "GET" "/invoices"
test_endpoint "Estimates" "GET" "/estimates"
test_endpoint "Taxes" "GET" "/taxes"
test_endpoint "Expenses" "GET" "/expenses"

echo ""
echo "Step 4: Testing Accounting Module Endpoints"
echo "========================================="
test_endpoint "Budgets" "GET" "/budgets"
test_endpoint "Budget Categories" "GET" "/budget-categories"

echo ""
echo "Step 5: Testing Auth Endpoints"
echo "========================================="
test_endpoint "Current User" "GET" "/auth/me"

echo ""
echo "========================================="
echo "Verification Complete!"
echo "========================================="
echo ""
echo "Total endpoints tested: 17"
echo "Server: $BASE_URL"
echo "Token: ${TOKEN:0:10}..."
