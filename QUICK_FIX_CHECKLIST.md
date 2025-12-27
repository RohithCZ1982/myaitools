# Quick Fix Checklist - Form Not Saving Data

Follow these steps in order to fix the issue:

## ✅ Step 1: Check Google Apps Script Configuration

1. Open your Google Apps Script project: https://script.google.com
2. Open the code editor
3. Find this line: `const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE';`
4. **CRITICAL**: Make sure it's NOT still set to `'YOUR_SPREADSHEET_ID_HERE'`
5. It should look like: `const SPREADSHEET_ID = '1a2b3c4d5e6f7g8h9i0j';` (your actual Sheet ID)

**To get your Spreadsheet ID:**
- Open your Google Sheet
- Look at the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit`
- Copy the part between `/d/` and `/edit`

## ✅ Step 2: Check Google Apps Script Logs

1. In Google Apps Script, click **View** > **Logs** (or press `Ctrl+Enter`)
2. Submit your form again
3. **Look for any red error messages**
4. Common errors you might see:
   - `SPREADSHEET_ID is not configured` → Go back to Step 1
   - `Exception: Invalid argument` → Your Sheet ID is wrong
   - `Exception: Access denied` → Go to Step 3

## ✅ Step 3: Re-authorize the Script

1. In Google Apps Script, go to **Deploy** > **Manage deployments**
2. Click the **✏️** (pencil/edit icon) next to your deployment
3. Click **"New version"**
4. Click **"Deploy"**
5. If prompted, click **"Authorize access"**
6. Choose your Google account
7. Click **"Advanced"** > **"Go to [Project Name] (unsafe)"**
8. Click **"Allow"**

## ✅ Step 4: Verify Sheet Headers

Open your Google Sheet and make sure Row 1 has these exact headers:
- Column A: `Timestamp`
- Column B: `Name`
- Column C: `Email`
- Column D: `Phone`
- Column E: `Message`
- Column F: `File Name`
- Column G: `File Link`

## ✅ Step 5: Test the Form

1. Open your form page
2. Press `F12` to open Developer Tools
3. Go to the **Console** tab
4. Fill out the form (just name and email is fine for testing)
5. Click Submit
6. **Check the console** - you should see debug messages
7. **Check your Google Sheet** - a new row should appear within a few seconds

## ✅ Step 6: Check Browser Console Errors

If Step 5 shows errors in the console:
- **"Failed to fetch"** → Check your internet connection
- **"CORS error"** → This is normal, ignore it
- **"Network error"** → Check the Web App URL is correct

## ✅ Step 7: Verify Web App URL

1. In Google Apps Script: **Deploy** > **Manage deployments**
2. Copy the Web App URL
3. In `custom-form.html`, find: `const GOOGLE_SCRIPT_URL = '...'`
4. Make sure the URLs match exactly

## ✅ Step 8: Test File Upload (if applicable)

1. Try uploading a small image (under 1MB)
2. Check Google Drive for a folder named "Form Uploads"
3. Check the Google Sheet - the File Link column should have a URL

## Still Not Working?

1. **Double-check SPREADSHEET_ID** - This is the #1 cause of issues
2. **Check execution logs**: View > Executions in Google Apps Script
3. **Try a test submission** with just name and email (no file)
4. **Check the Sheet permissions** - make sure it's shared with your Google account

## Most Common Issue

**90% of problems are caused by:**
- SPREADSHEET_ID not being set correctly in Google Apps Script
- Make sure it's your actual Sheet ID, not the placeholder text!

