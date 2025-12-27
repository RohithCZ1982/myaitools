# How to Check if Your Script is Running

Since you're getting a success message but no data in the sheet, let's verify what's happening:

## Step 1: Check Execution Logs (Most Important!)

1. Open your Google Apps Script project
2. Click **View** > **Executions** (NOT "Logs")
3. You should see a list of executions
4. Click on the most recent execution (from when you submitted the form)
5. Look at the status:
   - ✅ **Success (green)** = Script ran but data might not be saving
   - ❌ **Failed (red)** = Script had an error - click to see the error

## Step 2: Check Console Logs

1. In Google Apps Script, click **View** > **Logs** (or press `Ctrl+Enter`)
2. Submit the form again
3. Look for these messages in order:
   - `=== doPost called ===`
   - `Event exists: true`
   - `SPREADSHEET_ID: [your-id]`
   - `=== Data Processing ===`
   - `Received data object:`
   - `=== Opening Spreadsheet ===`
   - `✅ Row added successfully!`

**If you see errors instead, note what they say!**

## Step 3: Verify SPREADSHEET_ID

1. In your Google Apps Script code, find:
   ```javascript
   const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE';
   ```

2. **It MUST NOT say** `'YOUR_SPREADSHEET_ID_HERE'`

3. It should be something like:
   ```javascript
   const SPREADSHEET_ID = '1a2b3c4d5e6f7g8h9i0j';
   ```

4. **To get your Sheet ID:**
   - Open your Google Sheet
   - Look at URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
   - Copy the ID between `/d/` and `/edit`

## Step 4: Test Sheet Access Manually

1. Copy the `TEST_SCRIPT_SIMPLE.gs` code into your Google Apps Script project
2. Replace `YOUR_SPREADSHEET_ID_HERE` with your actual Sheet ID
3. Click the play button to run `testSheetAccess`
4. Check the logs - it will tell you if it can access your sheet
5. Check your Google Sheet - you should see a test row

## What to Look For

### If Executions shows "Failed":
- Click on it to see the error
- Most common: `SPREADSHEET_ID is not configured`
- Or: `Failed to open spreadsheet`

### If Executions shows "Success" but no data:
- Check the logs for the detailed messages
- Look for `✅ Row added successfully!`
- If you see this but no data in sheet, the Sheet ID might be wrong

### If you see NO executions:
- The request isn't reaching Google Apps Script
- Check that the Web App URL is correct in `custom-form.html`
- Make sure the script is deployed

## Quick Checklist

- [ ] SPREADSHEET_ID is set (not the placeholder)
- [ ] Script is deployed (Deploy > Manage deployments)
- [ ] Checked View > Executions for failed runs
- [ ] Checked View > Logs after submitting form
- [ ] Ran testSheetAccess() function manually

