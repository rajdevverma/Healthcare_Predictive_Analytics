#!/bin/bash
# Comprehensive Dashboard Data Flow Test

echo "======================================================================"
echo "COMPREHENSIVE DASHBOARD DATA FLOW TEST"
echo "======================================================================"

# Step 1: Login
echo ""
echo "[1] Logging in as doctor@healthcare.com..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor@healthcare.com","password":"doctor123"}' \
  -c /tmp/test_cookies.txt)

if echo "$LOGIN_RESPONSE" | grep -q '"success":true'; then
    echo "    ✓ Login successful"
    
    # Step 2: Add a test patient
    echo ""
    echo "[2] Adding a test patient..."
    PATIENT_RESPONSE=$(curl -s -X POST http://localhost:5001/api/patients/ \
      -H "Content-Type: application/json" \
      -b /tmp/test_cookies.txt \
      -d '{"name":"Test Patient","age":45,"gender":"Male","phone":"1234567890","email":"test@example.com"}')
    
    echo "    Response: $PATIENT_RESPONSE"
    
    if echo "$PATIENT_RESPONSE" | grep -q '"success":true'; then
        echo "    ✓ Patient added successfully"
        
        PATIENT_ID=$(echo "$PATIENT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['patient']['patient_id'])")
        echo "    Patient ID: $PATIENT_ID"
        
        # Step 3: Make a prediction
        echo ""
        echo "[3] Making a heart disease prediction..."
        PREDICT_RESPONSE=$(curl -s -X POST http://localhost:5001/api/predict/heart \
          -H "Content-Type: application/json" \
          -b /tmp/test_cookies.txt \
          -d "{\"patient_id\":\"$PATIENT_ID\",\"patient_name\":\"Test Patient\",\"age\":45,\"sex\":1,\"cp\":2,\"trestbps\":130,\"chol\":250,\"fbs\":0,\"restecg\":1,\"thalach\":150,\"exang\":0,\"oldpeak\":2.5,\"slope\":1,\"ca\":1,\"thal\":2}")
        
        echo "    Response: $PREDICT_RESPONSE"
        
        if echo "$PREDICT_RESPONSE" | grep -q '"success":true'; then
            echo "    ✓ Prediction made successfully"
            
            # Step 4: Get dashboard statistics
            echo ""
            echo "[4] Fetching dashboard statistics..."
            STATS_RESPONSE=$(curl -s -X GET http://localhost:5001/api/patients/stats \
              -H "Content-Type: application/json" \
              -b /tmp/test_cookies.txt)
            
            echo ""
            echo "======================================================================"
            echo "DASHBOARD STATISTICS:"
            echo "======================================================================"
            echo "$STATS_RESPONSE" | python3 -m json.tool
            
            # Extract and display values
            TOTAL_PATIENTS=$(echo "$STATS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['statistics']['total_patients'])")
            TOTAL_PREDICTIONS=$(echo "$STATS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['statistics']['total_predictions'])")
            
            echo ""
            echo "======================================================================"
            echo "VERIFICATION RESULTS:"
            echo "======================================================================"
            echo "  Total Patients:      $TOTAL_PATIENTS (Expected: >= 1)"
            echo "  Total Predictions:   $TOTAL_PREDICTIONS (Expected: >= 1)"
            
            if [ "$TOTAL_PATIENTS" -ge 1 ] && [ "$TOTAL_PREDICTIONS" -ge 1 ]; then
                echo ""
                echo "✅ SUCCESS! Dashboard displays REAL DATABASE DATA"
                echo "✅ Data flow verified: MySQL → Flask API → Dashboard"
                echo "======================================================================"
                exit 0
            else
                echo ""
                echo "❌ FAILED: Dashboard still showing zeros"
                echo "======================================================================"
                exit 1
            fi
        else
            echo "    ✗ Prediction failed"
            exit 1
        fi
    else
        echo "    ✗ Failed to add patient"
        exit 1
    fi
else
    echo "    ✗ Login failed"
    exit 1
fi
