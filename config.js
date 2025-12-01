// ============================================
// API KEY CONFIGURATION
// ============================================
// This file contains the API key configuration for all pages
// 
// To update your API key:
// 1. Get your API key from Google Cloud Console
// 2. Encode it using: btoa("YOUR_API_KEY") in browser console
// 3. Paste the encoded key below
// ============================================

// Google Generative AI API Key (for Assignment Generator and List Models)
const CONFIG = {
    // Encoded API key (use btoa("YOUR_API_KEY") in browser console to encode)
    encodedApiKey: "QUl6YVN5QTFYakJKVkdYYjR0QkswV2gyLVA0OVBqZjhWRFkzRjln",
    
    // Decode the API key
    getApiKey: function() {
        return atob(this.encodedApiKey);
    }
};

// Google Imagen API Key (for Poster Generator - can be same or different)
const IMAGEN_CONFIG = {
    // Encoded API key (use btoa("YOUR_API_KEY") in browser console to encode)
    encodedApiKey: "QUl6YVN5QTFYakJKVkdYYjR0QkswV2gyLVA0OVBqZjhWRFkzRjln",
    
    // Decode the API key
    getApiKey: function() {
        return atob(this.encodedApiKey);
    }
};

