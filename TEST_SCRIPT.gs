/**
 * Quick Test Script - Add this to your Google Apps Script project
 * to test if data is being received
 * 
 * Instructions:
 * 1. Copy this entire function into your Google Apps Script project
 * 2. Run it manually (click the play button) to test
 * 3. Check the logs (View > Logs)
 */

function testDoPost() {
  // Simulate a POST request with sample data
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
    },
    parameter: {}
  };
  
  // Call the doPost function
  const result = doPost(mockEvent);
  
  // Log the result
  console.log('Test result:', result.getContent());
  
  // Check the sheet
  const sheet = SpreadsheetApp.openById('YOUR_SPREADSHEET_ID_HERE').getActiveSheet();
  const lastRow = sheet.getLastRow();
  console.log('Last row in sheet:', lastRow);
  console.log('Last row data:', sheet.getRange(lastRow, 1, 1, 7).getValues());
}

