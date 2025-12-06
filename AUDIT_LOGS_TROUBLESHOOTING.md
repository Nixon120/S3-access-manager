# 🔍 Audit Logs Troubleshooting Guide

## Current Status

✅ **Audit logs ARE being created** - Database has 51 logs
✅ **Backend API is working** - Returns 200 OK
❓ **Frontend may not be displaying them** - Need to check browser console

---

## 🧪 How to Diagnose

### Step 1: Check Browser Console

1. **Login as admin**
2. **Open browser console** (F12 → Console tab)
3. **Look for these logs**:
   ```
   Stats Response: {total_users: 5, active_users: 5, ...}
   Recent Activity: [array of logs]
   ```

4. **What to look for**:
   - ✅ If `Recent Activity` shows an array with objects → Backend is working!
   - ❌ If `Recent Activity` is empty `[]` → Backend issue
   - ❌ If you see an error → API or auth issue

### Step 2: Check Database Directly

```bash
docker-compose exec db psql -U s3manager -d s3manager -c "
SELECT 
    id, 
    user_id, 
    action, 
    bucket name,
    status,
    created_at 
FROM audit_logs 
ORDER BY created_at DESC 
LIMIT 10;
"
```

**Expected**: Should show 10 recent log entries

### Step 3: Test API Directly

Open browser and go to:
```
http://localhost:8000/docs
```

1. Click on **/api/v1/audit/stats** (GET)
2. Click "Try it out"
3. Click "Execute"

**Expected**: Should see JSON response with `recent_activity` array

---

## 🐛 Common Issues & Fixes

### Issue 1: "No recent activity found" Message

**Cause**: The `recent_activity` array is empty

**Fix**: Check if there are actually logs in the database:

```bash
docker-compose exec db psql -U s3manager -d s3manager -c "SELECT COUNT(*) FROM audit_logs;"
```

If count is 0, logs aren't being created. If count > 0, there's an issue with the API.

---

### Issue 2: Frontend Shows Loading Forever

**Cause**: API call is failing or hanging

**Fix**:

1. Check browser console for errors
2. Check if the user is logged in as admin
3. Verify the API endpoint is accessible:
   ```bash
   curl http://localhost:8000/api/v1/audit/stats
   ```

---

### Issue 3: "Failed to load dashboard data" Error

**Cause**: API authentication issue or backend error

**Fix**:

1. **Check backend logs**:
   ```bash
   docker-compose logs --tail=50 backend | findstr ERROR
   ```

2. **Restart backend**:
   ```bash
   docker-compose restart backend
   ```

3. **Refresh browser** (Ctrl+F5)

---

### Issue 4: Logs Exist but Don't Display

**Cause**: Frontend/backend data mismatch (e.g., metadata field issue)

**This was already fixed** in the code by manually creating `AuditLogResponse` objects.

**Verify the fix is applied**:

```bash
# Check if the fix is in place
docker-compose exec backend cat /app/app/api/audit.py | findstr -A 10 "recent_activity ="
```

Should show the manual object creation loop.

---

## 📊 What the Dashboard Should Show

### Admin Dashboard Stats Cards:

| Card | Value | Description |
|------|-------|-------------|
| Users | Number | Total users in system |
| Buckets | Number | Unique buckets with permissions |
| Permissions | Number | Total permission entries |
| Activity | Number | Count of recent activity logs |

### Recent Activity List:

Each entry should show:
- **Action** (e.g., "list", "upload", "download")
- **Bucket/Key** (e.g., "envexis.com/input/file.txt")
- **User ID** (which user performed the action)
- **Timestamp** (when it happened)
- **Status Chip** (green for success, red for failure)

---

## 🔧 Manual Testing Steps

### Test 1: Trigger Some Activity

1. **Login as test user**
2. **Browse a bucket** (creates a "list" log)
3. **Try to upload a file** (creates "upload_initiated" and "upload" logs)
4. **Logout**
5. **Login as admin**
6. **Refresh dashboard**
7. **Should see the new activity**

### Test 2: Check API Response

1. **Open browser DevTools** (F12)
2. **Go to Network tab**
3. **Refresh admin dashboard**
4. **Find the request to** `/api/v1/audit/stats`
5. **Click on it**
6. **Check the Response tab**

**Expected Response**:
```json
{
  "total_users": 5,
  "active_users": 5,
  "total_buckets": 1,
  "total_permissions": 1,
  "recent_activity": [
    {
      "id": 51,
      "user_id": 5,
      "action": "list",
      "bucket_name": "envexis.com",
      "object_key": "input/",
      "status": "success",
      "created_at": "2025-12-05T18:37:04.915853Z"
    },
    ...
  ]
}
```

---

## ✅ Verification Checklist

- [ ] Logs exist in database (`SELECT COUNT(*) FROM audit_logs;` > 0)
- [ ] Backend API returns 200 OK (`curl http://localhost:8000/api/v1/audit/stats`)
- [ ] Browser console shows stats data (`console.log` output)
- [ ] Browser console shows `recent_activity` array with objects
- [ ] Dashboard shows "Recent Activity" section
- [ ] Either logs are displayed OR "No recent activity found" message shows
- [ ] No JavaScript errors in browser console
- [ ] No server errors in backend logs

---

## 🆘 If Still Not Working

1. **Refresh the page** (Ctrl+F5 for hard refresh)
2. **Clear browser cache**
3. **Check browser console** for the console.log output I added
4. **Restart backend**: `docker-compose restart backend`
5. **Check if user is actually admin**: `SELECT email, is_admin FROM users;`
6. **Send me the browser console output** so I can see what data is being received

---

## 📝 What I Changed

1. ✅ Added check for empty `recent_activity` array
2. ✅ Show "No recent activity found" message when empty
3. ✅ Added `console.log` to see what data is received
4. ✅ Better error handling in the dashboard

---

**The audit logs system is working correctly. If you still don't see logs, please:**

1. Open browser console (F12)
2. Refresh the admin dashboard
3. Look for the `console.log` output
4. Tell me what you see!

The console will show exactly what data the frontend is receiving from the backend.
