# S3 Access Manager - Upload Workflow & Permission Enforcement Guide

## Table of Contents
1. [Overview](#overview)
2. [Permission Enforcement Logic](#permission-enforcement-logic)
3. [User Upload Workflow](#user-upload-workflow)
4. [Folder Navigation System](#folder-navigation-system)
5. [Security & Validation](#security--validation)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The S3 Access Manager implements a **strict prefix-based permission system** that ensures users can ONLY upload files to their assigned S3 prefixes (folders). This document explains exactly how the system works and how users interact with it.

### Key Features

✅ **Folder Navigation** - Browse subfolders like Windows Explorer
✅ **Context-Aware Uploads** - Upload to any subfolder you're viewing
✅ **Strict Enforcement** - Users CANNOT upload outside their prefix
✅ **Backend Validation** - Every upload checked automatically
✅ **Complete Audit Trail** - Every attempt logged
✅ **Visual Feedback** - Always know where you are

---

## Permission Enforcement Logic

### How It Works

Every permission has a **prefix** (folder path) that defines where a user can access files. The system uses simple **prefix matching** to enforce access:

```python
# The Golden Rule
if upload_path.startswith(user_prefix):
    ✅ ALLOWED
else:
    ❌ BLOCKED (403 Forbidden + Logged)
```

### Real Example

**Admin creates permission**:
```
User: alice@partner-a.com
Bucket: partner-data
Prefix: partner-a/uploads/
Permissions: ✓ Write ✓ List
```

**What Alice Can Do**:

✅ **ALLOWED** (all within prefix):
```
partner-data/partner-a/uploads/file.pdf
partner-data/partner-a/uploads/2024/file.pdf
partner-data/partner-a/uploads/2024/january/file.pdf
partner-data/partner-a/uploads/any/deep/path/file.pdf
```

❌ **BLOCKED** (outside prefix):
```
partner-data/file.pdf                    (root - outside)
partner-data/partner-b/uploads/file.pdf  (different prefix)
partner-data/partner-a/reports/file.pdf  (sibling folder)
```

### Backend Validation Code

Every upload request goes through this validation:

```python
# From backend/app/api/s3.py
def check_permission(user, bucket, object_key, action):
    permissions = get_user_permissions(user, bucket)
    
    for perm in permissions:
        if object_key.startswith(perm.prefix):
            if action == "write" and perm.can_write:
                return True  # ✅ ALLOWED
    
    raise HTTPException(403, "Access denied")  # ❌ BLOCKED
```

**This check happens on EVERY upload request. Cannot be bypassed.**

---

## User Upload Workflow

### Step-by-Step Process

#### 1. User Logs In

Dashboard shows assigned buckets:
```
📁 Your Buckets
  └─ partner-data / partner-a/uploads/
```

#### 2. User Selects Bucket

Clicks: `partner-data / partner-a/uploads/`

Sees:
```
🏠 partner-a/uploads/
Current location: partner-data/partner-a/uploads/

📁 2024
📁 invoices
📄 readme.txt
```

#### 3. User Navigates to Subfolder

**Clicks folder**: `2024`

**Breadcrumb updates**: `🏠 partner-a/uploads/ > 2024`

**Sees**:
```
📁 january
📁 february
📁 march
📄 quarterly-report.pdf
```

**Clicks folder**: `january`

**Breadcrumb updates**: `🏠 partner-a/uploads/ > 2024 > january`

#### 4. User Uploads Files

**Clicks**: `[Upload Files]`

**Dialog shows**:
```
┌──────────────────────────────────────────────┐
│ Upload Files                                 │
├──────────────────────────────────────────────┤
│ 📁 Upload destination:                       │
│    partner-data/partner-a/uploads/2024/january/ │
├──────────────────────────────────────────────┤
│ [Drag and drop files here]                   │
│                                              │
│ or click to browse files                     │
└──────────────────────────────────────────────┘
```

**User drags 3 files**:
- invoice-001.pdf
- invoice-002.pdf
- summary.xlsx

**Files upload to**:
```
s3://partner-data/partner-a/uploads/2024/january/invoice-001.pdf
s3://partner-data/partner-a/uploads/2024/january/invoice-002.pdf
s3://partner-data/partner-a/uploads/2024/january/summary.xlsx
```

**Backend validates**:
```python
"partner-a/uploads/2024/january/invoice-001.pdf".startswith("partner-a/uploads/")
# True → ✅ ALLOWED
```

**Audit log created**:
```
user: alice@partner-a.com
action: upload
bucket: partner-data
object_key: partner-a/uploads/2024/january/invoice-001.pdf
status: success ✅
timestamp: 2024-12-05 00:55:23
```

#### 5. User Navigates Back

**Clicks breadcrumb**: `2024` (goes back one level)
**Now at**: `partner-a/uploads/2024/`

**Clicks breadcrumb**: `🏠 partner-a/uploads/` (goes to root)
**Now at**: `partner-a/uploads/`

---

## Folder Navigation System

### Visual Interface

```
┌──────────────────────────────────────────────────────────────┐
│ 🏠 partner-a/uploads/ > 2024 > january          ← Breadcrumb │
│ Current location: partner-data/partner-a/uploads/2024/january/ │
├──────────────────────────────────────────────────────────────┤
│ 📁 2 folder(s)  📄 5 file(s)                      [↻]        │
├──────────────────────────────────────────────────────────────┤
│ Name              Size      Modified          Actions        │
├──────────────────────────────────────────────────────────────┤
│ 📁 invoices      —         —                 Folder          │ ← Click to enter
│ 📁 reports       —         —                 Folder          │ ← Click to enter  
│ 📄 file1.pdf     2.3 MB    Dec 1, 2024       [↓] [🗑]       │
│ 📄 file2.xlsx    500 KB    Nov 28, 2024      [↓] [🗑]       │
└──────────────────────────────────────────────────────────────┘
                          [Upload Files]
```

### Features

#### Breadcrumb Navigation
- Click any level to go back
- Home icon (🏠) returns to root
- Shows full path hierarchy

#### Folder Display
- Folders shown with 📁 icon
- Files shown with 📄 icon
- Folders listed first (alphabetically)
- Files listed second (alphabetically)

#### Current Location
- Always displays full path
- Shows folder/file counts
- Visual feedback of position

#### Click to Navigate
- Click folders to enter them
- Natural navigation like file explorer
- Path updates automatically

---

## Security & Validation

### 1. Backend Validation

Every upload is validated:

```python
def validate_upload(user, bucket, object_key):
    # Get user's permissions for this bucket
    permissions = db.query(Permission).filter(
        Permission.user_id == user.id,
        Permission.bucket_name == bucket,
        Permission.can_write == True
    ).all()
    
    # Check if object_key starts with any allowed prefix
    for perm in permissions:
        if object_key.startswith(perm.prefix):
            return True  # ✅ ALLOWED
    
    # Log the blocked attempt
    audit_log = AuditLog(
        user_id=user.id,
        action="upload_blocked",
        bucket_name=bucket,
        object_key=object_key,
        status="blocked",
        error_message="No write permission for this prefix"
    )
    db.add(audit_log)
    db.commit()
    
    raise HTTPException(403, "Access denied")  # ❌ BLOCKED
```

### 2. No Bypass Possible

**Even if user tries direct API call**:

```bash
curl -X POST https://app.com/api/v1/s3/presigned-url \
  -H "Authorization: Bearer alice_token" \
  -d '{"bucket_name": "partner-data",
       "object_key": "partner-b/uploads/hack.pdf"}'
```

**Response**:
```json
{
  "status_code": 403,
  "detail": "No write permission for: partner-data/partner-b/uploads/hack.pdf"
}
```

### 3. Complete Audit Trail

Every attempt (success AND failure) is logged:

```
✅ alice uploaded to partner-a/uploads/2024/file.pdf - SUCCESS
❌ alice tried to upload to partner-b/uploads/file.pdf - BLOCKED
✅ alice downloaded from partner-a/uploads/report.pdf - SUCCESS
❌ alice tried to delete partner-a/reports/file.pdf - BLOCKED
```

Admins can view all activity in the Audit Logs page.

---

## Best Practices

### 1. Use Clear Prefixes

```
✅ GOOD:
   "partner-a/uploads/"
   "radiology-dept/patient-scans/"
   "finance/invoices/2024/"

❌ BAD:
   "" (empty = full bucket access!)
   "data/" (too vague)
```

### 2. Organize by Partner/Department

Structure your bucket:
```
partner-a/
  ├─ uploads/       ← Partner writes here
  ├─ processed/     ← Partner reads from here
  └─ archive/       ← No access

partner-b/
  ├─ uploads/
  └─ downloads/
```

Then assign:
```
Alice (Partner A) → "partner-a/uploads/" (Write)
Alice (Partner A) → "partner-a/processed/" (Read)
Bob (Partner B)   → "partner-b/uploads/" (Write)
```

### 3. Use Date-Based Subfolders

```
partner-a/uploads/
  ├─ 2024/
  │   ├─ 01-january/
  │   ├─ 02-february/
  │   └─ 03-march/
  └─ 2025/
      └─ 01-january/
```

Users can naturally navigate by date!

### 4. Test Permissions Before Granting

Use the "Test Connection" feature in S3 Connections to verify AWS credentials work before assigning permissions.

---

## Troubleshooting

### User Can't Upload Files

**Symptom**: Upload button is grayed out or upload fails

**Possible Causes**:
1. User doesn't have `can_write` permission
2. User is trying to upload outside their prefix
3. AWS credentials are invalid

**Solution**:
1. Check permission in Admin → Permissions
2. Verify `can_write` is checked
3. Test the S3 connection in Admin → S3 Connections

### User Can't See Folders

**Symptom**: Folders don't appear in file browser

**Possible Causes**:
1. No objects exist in subfolders
2. Prefix doesn't match folder structure

**Solution**:
1. Upload a file to create the folder structure
2. Verify prefix ends with `/` (e.g., `partner-a/uploads/`)

### Upload Fails with 403 Error

**Symptom**: "Access denied" or "No write permission"

**Cause**: User is trying to upload outside their assigned prefix

**Solution**:
1. Check the upload destination path
2. Verify it starts with the user's assigned prefix
3. Check Audit Logs to see the exact path that was blocked

### Files Upload to Wrong Location

**Symptom**: Files appear in unexpected folder

**Cause**: User uploaded from wrong navigation level

**Solution**:
1. Check breadcrumb before uploading
2. Navigate to correct folder first
3. Verify "Upload destination" in upload dialog

---

## S3 Connections Management

### Overview

The S3 Connections feature allows managing multiple AWS accounts from a single interface.

### Creating a Connection

1. Navigate to **Admin → S3 Connections**
2. Click **Add Connection**
3. Fill in the form:
   - **Connection Name**: e.g., "Production Account"
   - **AWS Account ID**: 12-digit account ID
   - **Region**: e.g., us-east-1
   - **Auth Method**: Access Keys or IAM Role
   - **Credentials**: Access Key ID and Secret (if using Access Keys)
4. Click **Test Connection** to verify
5. Click **Create** to save

### Using Connections in Permissions

When creating a permission:
1. Select the **S3 Connection** from dropdown
2. Or leave as "Default" to use environment variables
3. Specify bucket name and prefix as usual

### Connection Status

- **Active** (green): Connection is enabled
- **Inactive** (gray): Connection is disabled

### Testing Connections

The "Test Connection" button validates:
- AWS credentials are correct
- Can list buckets in the account
- Returns bucket count on success

---

## Summary

### The Bottom Line

**Users can organize files in subfolders as much as they want, but ONLY within their assigned prefix. The system enforces this automatically at the backend level. Period.**

```python
# The Golden Rule
if upload_path.startswith(user_prefix):
    ✅ ALLOWED
else:
    ❌ BLOCKED (403 + Logged)
```

**This is enforced on EVERY upload request. Cannot be bypassed. Fully logged.**

### Key Takeaways

1. ✅ **Folder navigation** works like Windows Explorer
2. ✅ **Upload to any subfolder** you're viewing
3. ✅ **Strict prefix enforcement** - no exceptions
4. ✅ **Backend validation** - every request checked
5. ✅ **Complete audit trail** - all attempts logged
6. ✅ **Multi-account support** - manage 50+ AWS accounts

---

## Additional Resources

- **Admin Guide**: See `README.md` for setup instructions
- **API Documentation**: Visit `/docs` endpoint for API reference
- **Audit Logs**: Admin → Audit Logs for activity monitoring
- **Support**: Contact your system administrator

---

**Version**: 1.0.0
**Last Updated**: December 2024
