/**
 * SIMPLE TEST FUNCTION
 * 
 * Copy this function into your Google Apps Script project
 * Run it manually to test if the script can access your sheet
 */

function testSheetAccess() {
  // REPLACE THIS with your actual Spreadsheet ID
  const TEST_SHEET_ID = 'YOUR_SPREADSHEET_ID_HERE';
  
  try {
    console.log('Testing spreadsheet access...');
    console.log('Sheet ID:', TEST_SHEET_ID);
    
    // Try to open the sheet
    const spreadsheet = SpreadsheetApp.openById(TEST_SHEET_ID);
    const sheet = spreadsheet.getActiveSheet();
    
    console.log('✅ Sheet opened successfully!');
    console.log('Sheet name:', sheet.getName());
    console.log('Current last row:', sheet.getLastRow());
    
    // Try to add a test row
    const testData = [
      new Date(),
      'Test Name',
      'test@example.com',
      '1234567890',
      'This is a test message',
      '',
      ''
    ];
    
    sheet.appendRow(testData);
    console.log('✅ Test row added successfully!');
    console.log('New last row:', sheet.getLastRow());
    
    return 'SUCCESS: Sheet access works! Check your sheet for the test row.';
    
  } catch (error) {
    console.error('❌ ERROR:', error.toString());
    return 'ERROR: ' + error.toString();
  }
}

