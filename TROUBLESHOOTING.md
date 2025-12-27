# Troubleshooting Guide - Form Not Saving Data

If your form submissions aren't appearing in Google Sheets or files aren't uploading, follow these steps:

## Step 1: Verify Google Apps Script Configuration

### Check SPREADSHEET_ID
1. Open your Google Apps Script project
2. Make sure `SPREADSHEET_ID` is set (not `'YOUR_SPREADSHEET_ID_HERE'`)
3. To get your Spreadsheet ID:
   - Open your Google Sheet
   - Look at the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit`
   - Copy the part between `/d/` and `/edit`

### Check Web App URL
1. In Google Apps Script, go to **Deploy** > **Manage deployments**
2. Copy the Web App URL
3. In `custom-form.html`, make sure `GOOGLE_SCRIPT_URL` matches exactly

## Step 2: Check Google Apps Script Logs

1. In Google Apps Script, click **View** > **Logs** (or press `Ctrl+Enter`)
2. Submit the form again
3. Check the logs for any error messages
4. Common errors:
   - `SPREADSHEET_ID is not configured` → Update the SPREADSHEET_ID
   - `Exception: Invalid argument` → Check that the Sheet ID is correct
   - `Exception: Access denied` → Re-authorize the script

## Step 3: Test the Web App Directly

1. Copy your Web App URL
2. Open it in a new browser tab
3. You should see: "Form submission endpoint is ready. Use POST method to submit data."
4. If you see an error, the deployment might be incorrect

## Step 4: Check Browser Console

1. Open your form page
2. Press `F12` to open Developer Tools
3. Go to the **Console** tab
4. Submit the form
5. Look for any red error messages
6. Common errors:
   - `CORS policy` → This is normal, data should still save
   - `Failed to fetch` → Check the Web App URL is correct
   - `Network error` → Check your internet connection

## Step 5: Verify Sheet Permissions

1. Open your Google Sheet
2. Click **Share** (top right)
3. Make sure the Google account running the Apps Script has **Editor** access
4. The script runs as "Me" (your account), so you need access

## Step 6: Re-authorize the Script

If you've made changes or see authorization errors:

1. In Google Apps Script, go to **Deploy** > **Manage deployments**
2. Click the **✏️** (edit) icon
3. Click **New version**
4. Click **Deploy**
5. You may be prompted to authorize again - click **Authorize access**
6. Click **Advanced** > **Go to [Project Name] (unsafe)**
7. Click **Allow**

## Step 7: Check Sheet Headers

Make sure your Google Sheet has these exact column headers in Row 1:
- Column A: `Timestamp`
- Column B: `Name`
- Column C: `Email`
- Column D: `Phone`
- Column E: `Message`
- Column F: `File Name`
- Column G: `File Link`

## Step 8: Test with a Simple Submission

Try submitting the form with:
- Just Name and Email (required fields)
- No file upload first
- Check if basic data appears in the sheet

## Step 9: Check File Upload Issues

If files aren't uploading:

1. Check Google Apps Script logs for file upload errors
2. Verify the `DRIVE_FOLDER_NAME` is set correctly
3. Check your Google Drive for a folder named "Form Uploads"
4. Make sure the file size is under 25MB
5. Try with a small image first (under 1MB)

## Step 10: Manual Test of Apps Script

You can test the script manually:

1. In Google Apps Script, create a test function:
```javascript
function testSubmission() {
  const testData = {
    timestamp: new Date().toISOString(),
    name: 'Test User',
    email: 'test@example.com',
    phone: '1234567890',
    message: 'Test message'
  };
  
  const mockEvent = {
    postData: {
      type: 'application/json',
      contents: JSON.stringify(testData)
    }
  };
  
  doPost(mockEvent);
}
```

2. Run this function (click the play button)
3. Check your Google Sheet - you should see a test row
4. If this works, the issue is with the form submission, not the script

## Common Issues and Solutions

### Issue: "SPREADSHEET_ID is not configured"
**Solution**: Update the `SPREADSHEET_ID` constant in your Google Apps Script code

### Issue: Data appears but file doesn't upload
**Solution**: 
- Check file size (must be under 25MB)
- Check Google Apps Script logs for file upload errors
- Verify Drive folder permissions

### Issue: CORS errors in browser console
**Solution**: This is normal! Google Apps Script has CORS restrictions. The data should still save - check your Google Sheet to confirm.

### Issue: "Access denied" or "Permission denied"
**Solution**: 
- Re-authorize the script (Step 6)
- Make sure the Sheet is shared with your Google account
- Check that "Execute as" is set to "Me" in deployment settings

### Issue: Form submits but nothing happens
**Solution**:
- Check browser console (F12) for JavaScript errors
- Verify the Web App URL is correct
- Check Google Apps Script execution logs
- Make sure you're using the latest deployment version

## Still Not Working?

1. **Double-check all configuration**:
   - ✅ SPREADSHEET_ID is set correctly
   - ✅ Web App URL is correct in custom-form.html
   - ✅ Sheet has correct column headers
   - ✅ Script is deployed and authorized

2. **Check the execution log**:
   - In Google Apps Script: View > Executions
   - Look for failed executions and error details

3. **Try redeploying**:
   - Deploy > Manage deployments
   - Edit > New version > Deploy

4. **Test with a fresh deployment**:
   - Create a new deployment
   - Update the URL in custom-form.html
   - Test again
