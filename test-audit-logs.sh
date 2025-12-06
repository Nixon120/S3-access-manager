#!/bin/bash

echo "======================================"
echo "S3 Access Manager - Audit Logs Diagnostic"
echo "======================================"
echo ""

# Test 1: Check if logs exist in database
echo "Test 1: Checking database for audit logs..."
docker-compose exec -T db psql -U s3manager -d s3manager -c "SELECT COUNT(*) as total_logs FROM audit_logs;" 2>/dev/null
echo ""

# Test 2: Show sample logs
echo "Test 2: Sample audit logs from database..."
docker-compose exec -T db psql -U s3manager -d s3manager -c "SELECT id, action, bucket_name, status, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 3;" 2>/dev/null
echo ""

# Test 3: Check if backend is running
echo "Test 3: Checking if backend is responding..."
curl -s http://localhost:8000/docs > /dev/null && echo "✅ Backend is running" || echo "❌ Backend is NOT running"
echo ""

# Test 4: Show recent backend logs
echo "Test 4: Recent backend logs..."
docker-compose logs --tail=5 backend 2>/dev/null | grep -i "error\|info" | tail -5
echo ""

# Test 5: Check frontend container
echo "Test 5: Checking frontend status..."
docker-compose ps frontend 2>/dev/null
echo ""

echo "======================================"
echo "Next Steps:"
echo "======================================"
echo "1. Login to admin dashboard at http://localhost:3000"
echo "2. Open browser console (F12)"
echo "3. Check for any red errors"
echo "4. Look for 'Stats Response:' log message"
echo "5. Share what you see in the console"
echo ""
