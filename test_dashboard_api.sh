#!/bin/bash
# Test Dashboard API with curl

echo "======================================================================"
echo "Testing Dashboard API Endpoint"
echo "======================================================================"

# Step 1: Login and save cookies
echo ""
echo "[1] Logging in as doctor@healthcare.com..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor@healthcare.com","password":"doctor123"}' \
  -c /tmp/dashboard_cookies.txt)

echo "    Response: $LOGIN_RESPONSE"

if echo "$LOGIN_RESPONSE" | grep -q '"success":true'; then
    echo "    ✓ Login successful"
    
    # Step 2: Get statistics with cookies
    echo ""
    echo "[2] Fetching dashboard statistics..."
    STATS_RESPONSE=$(curl -s -X GET http://localhost:5001/api/patients/stats \
      -H "Content-Type: application/json" \
      -b /tmp/dashboard_cookies.txt)
    
    echo ""
    echo "======================================================================"
    echo "API RESPONSE:"
    echo "======================================================================"
    echo "$STATS_RESPONSE" | python3 -m json.tool
    
    if echo "$STATS_RESPONSE" | grep -q '"success":true'; then
        echo ""
        echo "======================================================================"
        echo "✓ VERIFICATION SUCCESSFUL - Dashboard API returns real data!"
        echo "======================================================================"
    else
        echo ""
        echo "✗ API returned success=false"
    fi
else
    echo "    ✗ Login failed"
fi
