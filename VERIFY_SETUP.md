# Quick Verification Checklist

Follow these steps to ensure everything is configured correctly:

## ✅ Step 1: Check SPREADSHEET_ID in Google Apps Script

1. Open your Google Apps Script project
2. Look at the top of the code file for this line:
   ```javascript
   const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE';
   ```

3. **CRITICAL**: It should NOT say `'YOUR_SPREADSHEET_ID_HERE'`
   
4. It should look like this (with your actual ID):
   ```javascript
   const SPREADSHEET_ID = '1a2b3c4d5e6f7g8h9i0j123456789';
   ```

5. **To get your Sheet ID:**
   - Open your Google Sheet
   - Look at the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
   - Copy the part between `/d/` and `/edit`
   - Paste it between the quotes in the script

## ✅ Step 2: Verify Sheet Headers

Open your Google Sheet and make sure Row 1 has these columns:
- Column A: `Timestamp`
- Column B: `Name`  
- Column C: `Email`
- Column D: `Phone`
- Column E: `Message`
- Column F: `File Name`
- Column G: `File Link`

## ✅ Step 3: Redeploy the Script

1. In Google Apps Script: **Deploy** > **Manage deployments**
2. Click the **✏️** (edit/pencil icon)
3. Click **"New version"**
4. Click **"Deploy"**
5. You may need to authorize again - click **"Authorize access"**

## ✅ Step 4: Test the Form

1. Open your `custom-form.html` page
2. Fill out the form (name and email at minimum)
3. Click Submit
4. Wait 2-3 seconds
5. Check your Google Sheet - you should see a new row

## ✅ Step 5: Check Google Apps Script Logs

If data still doesn't appear:

1. In Google Apps Script: **View** > **Logs** (or press `Ctrl+Enter`)
2. Submit the form again
3. Look at the logs - you should see:
   - `"Received data:"` followed by your form data
   - `"Row added to sheet successfully"`

4. If you see errors, note what they say

## Most Common Issue

**90% of the time, the problem is:**
- `SPREADSHEET_ID` is still set to `'YOUR_SPREADSHEET_ID_HERE'`
- It needs to be your actual Google Sheet ID

Fix this first, then redeploy!

