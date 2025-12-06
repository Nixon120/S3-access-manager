Write-Host "======================================" -ForegroundColor Cyan
Write-Host "S3 Access Manager - Audit Logs Diagnostic" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if logs exist in database
Write-Host "Test 1: Checking database for audit logs..." -ForegroundColor Yellow
docker-compose exec -T db psql -U s3manager -d s3manager -c "SELECT COUNT(*) as total_logs FROM audit_logs;"
Write-Host ""

# Test 2: Show sample logs
Write-Host "Test 2: Sample audit logs from database..." -ForegroundColor Yellow
docker-compose exec -T db psql -U s3manager -d s3manager -c "SELECT id, action, bucket_name, status, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 3;"
Write-Host ""

# Test 3: Check containers
Write-Host "Test 3: Checking container status..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# Test 4: Test API endpoint directly
Write-Host "Test 4: Testing audit stats API endpoint..." -ForegroundColor Yellow
Write-Host "(Note: This requires admin authentication)" -ForegroundColor Gray
Write-Host ""

# Test 5: Show recent logs
Write-Host "Test 5: Recent backend logs (last 10 lines)..." -ForegroundColor Yellow
docker-compose logs --tail=10 backend
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "IMPORTANT: Browser Console Check" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please do the following:" -ForegroundColor Green
Write-Host "1. Open browser and go to: http://localhost:3000" -ForegroundColor White
Write-Host "2. Login as admin (nixonlauture@gmail.com)" -ForegroundColor White
Write-Host "3. Press F12 to open DevTools" -ForegroundColor White
Write-Host "4. Click on 'Console' tab" -ForegroundColor White
Write-Host "5. Look for these messages:" -ForegroundColor White
Write-Host "   - 'Stats Response: {...}'" -ForegroundColor Gray
Write-Host "   - 'Recent Activity: [...]'" -ForegroundColor Gray
Write-Host ""
Write-Host "6. Tell me what you see!" -ForegroundColor Yellow
Write-Host ""
