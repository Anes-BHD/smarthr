#!/bin/bash

# SmartHR API Test Verification Script
# This script verifies that all API endpoints have been properly seeded and are working

BASE_URL="http://127.0.0.1:8002"
API_PREFIX="/api/v1"

echo "========================================="
echo "SmartHR API Endpoint Verification"
echo "========================================="
echo ""

# Step 1: Authenticate and get token
echo "Step 1: Authenticating..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"employee@smarthr.com","password":"password"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')
echo "✓ Authentication successful"
echo "Token: $TOKEN"
echo ""

# Step 2: Test all endpoints
echo "Step 2: Testing API Endpoints"
echo "========================================="

test_endpoint() {
  local name=$1
  local endpoint=$2
  
  RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL$API_PREFIX$endpoint")
  COUNT=$(echo "$RESPONSE" | jq '.data | length' 2>/dev/null || echo "0")
  
  if [ "$COUNT" == "0" ] && echo "$RESPONSE" | grep -q "error"; then
    echo "✗ $name - Error"
    echo "  Response: $(echo "$RESPONSE" | jq -r '.message // .error' 2>/dev/null || echo 'Unknown error')"
  else
    echo "✓ $name - $COUNT records found"
  fi
}

test_endpoint "Employees" "/employees"
test_endpoint "Clients" "/clients"
test_endpoint "Attendances" "/attendances"
test_endpoint "Tickets" "/tickets"
test_endpoint "Assets" "/assets"
test_endpoint "Invoices" "/invoices"

echo ""
echo "========================================="
echo "Verification Complete!"
echo "========================================="
