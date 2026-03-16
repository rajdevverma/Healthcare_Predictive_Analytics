#!/bin/bash
# Simple test to verify dashboard stats for current user

echo "======================================================================"
echo "Dashboard Stats Test"
echo "======================================================================"

# Login and get stats
curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor@healthcare.com","password":"doctor123"}' \
  -c /tmp/quick_test.txt > /dev/null

echo ""
echo "Dashboard Statistics for doctor@healthcare.com:"
echo "----------------------------------------------------------------------"
curl -s -X GET http://localhost:5001/api/patients/stats \
  -H "Content-Type: application/json" \
  -b /tmp/quick_test.txt | python3 -m json.tool

echo ""
echo "======================================================================"
