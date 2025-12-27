# How to Check Logs in Google Apps Script

## Method 1: View Logs (Console Output)

1. **Open your Google Apps Script project**
   - Go to https://script.google.com
   - Open your project

2. **Submit your form** (from the HTML page)

3. **Open the Logs panel:**
   - Click on **"View"** menu at the top
   - Select **"Logs"**
   - OR press `Ctrl+Enter` (Windows) or `Cmd+Enter` (Mac)
   - OR click the bug icon (🐛) in the toolbar

4. **The logs panel will appear at the bottom** of the screen
   - If you don't see it, look for a panel/drawer at the bottom
   - You may need to drag it up to see it

5. **Refresh the logs:**
   - After submitting the form, click the **refresh button** (circular arrow) in the logs panel
   - Or click **View > Logs** again

## Method 2: View Executions (More Reliable)

This shows if the script ran and if it failed:

1. **Click "View" menu**
2. **Select "Executions"**
3. **You'll see a list of all script runs**
   - Green checkmark = Success
   - Red X = Failed
   - Clock icon = Running

4. **Click on an execution** to see details:
   - If it failed, you'll see the error message
   - If it succeeded, you can see execution time

## Method 3: Use Logger (Alternative)

If logs still don't show, add this to your script temporarily:

1. Add this line at the start of `doPost`:
```javascript
Logger.log('doPost called');
```

2. After running, go to **View > Logs** and you should see it

## Troubleshooting: Logs Not Showing

### If the logs panel is empty:

1. **Make sure you submitted the form** - logs only appear when the script runs
2. **Check the time filter** - make sure it's set to "All time" or recent time
3. **Refresh the page** - sometimes the logs don't update automatically
4. **Clear browser cache** - try refreshing the browser

### If you see "No logs":

1. The script might not be running at all
2. Check **View > Executions** instead
3. Make sure the script is deployed (Deploy > Manage deployments)

## What to Look For

After submitting the form, you should see logs like:

```
=== doPost called ===
Event exists: true
SPREADSHEET_ID: 1bhJZNV_WipJ7J4dk5nDus-y7hxk-cCAE0DO7UtXDMBo
=== Data Processing ===
Event parameters: [name, email, phone, message, timestamp]
Received data object: {name: "Test", email: "test@example.com", ...}
=== Opening Spreadsheet ===
Spreadsheet opened successfully. Sheet name: Sheet1
=== Adding Row to Sheet ===
✅ Row added successfully! New last row: 2
```

Or if there's an error, you'll see:
```
ERROR: SPREADSHEET_ID is not configured
```
or
```
ERROR opening spreadsheet: ...
```

## Quick Check Checklist

- [ ] Submitted the form from the HTML page
- [ ] Opened View > Logs (or pressed Ctrl+Enter)
- [ ] Checked View > Executions to see if script ran
- [ ] Refreshed the logs panel
- [ ] Checked that logs show recent time (not old logs)

## Still Not Working?

1. **Try View > Executions** - this is often more reliable
2. **Check that the script is deployed** - Deploy > Manage deployments
3. **Try running a simple test function** manually to see if logs work at all

