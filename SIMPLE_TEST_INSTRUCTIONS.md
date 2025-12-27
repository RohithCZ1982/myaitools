# Simple Test Instructions

## Quick Test - Run This Function Manually

1. **Open your Google Apps Script project**
   - Go to https://script.google.com
   - Open your project

2. **Find the `testFormSubmission` function**
   - Scroll down in your code
   - Look for a function called `testFormSubmission`

3. **Run the test:**
   - Click on the function name `testFormSubmission` in the function dropdown (top of the code editor)
   - OR select the function name in the code
   - Click the **▶️ Run** button (play icon) in the toolbar
   - OR press `Ctrl+R` (Windows) or `Cmd+R` (Mac)

4. **Authorize if prompted:**
   - Click "Review permissions"
   - Choose your Google account
   - Click "Advanced" > "Go to [Project Name] (unsafe)"
   - Click "Allow"

5. **Check the results:**
   - Look at the execution log at the bottom
   - You should see messages like:
     - ✅ Spreadsheet opened successfully!
     - ✅ Test row added successfully!
   - Check your Google Sheet - you should see a new test row

## What This Test Does

- ✅ Checks if SPREADSHEET_ID is configured
- ✅ Tests if it can open your Google Sheet
- ✅ Tests if it can add a row to the sheet
- ✅ Tests if the Drive folder is accessible

## If Test Passes But Form Still Doesn't Work

If the test works (you see a test row in your sheet), but the form still doesn't save data:

1. **Make sure the script is deployed:**
   - Go to **Deploy** > **Manage deployments**
   - Make sure there's a deployment listed
   - If not, create one (Deploy > New deployment > Web app)

2. **Check the Web App URL:**
   - In Deploy > Manage deployments, copy the Web App URL
   - Make sure it matches the URL in `custom-form.html`
   - The URL should end with `/exec`

3. **Test the actual form:**
   - Submit the form from your HTML page
   - Then check View > Executions (not Logs)
   - Look for a new execution entry

## If Test Fails

If you see an error:

- **"SPREADSHEET_ID is not configured"** → Make sure you've set the SPREADSHEET_ID constant at the top of your script
- **"Exception: Access denied"** → You need to authorize the script (click Allow when prompted)
- **"Exception: Invalid argument"** → The SPREADSHEET_ID might be wrong - check it again
- **"Exception: File not found"** → The Sheet ID doesn't exist or you don't have access to it

## Alternative: Test via Web App URL

You can also test by visiting the Web App URL directly:

1. Copy your Web App URL (from Deploy > Manage deployments)
2. Open it in a browser
3. You should see: "Form submission endpoint is ready. Use POST method to submit data."
4. This confirms the web app is deployed and accessible

