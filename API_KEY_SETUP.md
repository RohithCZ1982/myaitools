# How to Create a Google Imagen API Key

Follow these steps to get your Google Imagen API key:

## Step 1: Create a Google Cloud Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account (or create one if needed)

## Step 2: Create a New Project
1. Click on the project dropdown at the top of the page
2. Click **"New Project"**
3. Enter a project name (e.g., "AI Poster Generator")
4. Click **"Create"**
5. Wait for the project to be created, then select it from the dropdown

## Step 3: Enable the Imagen API
1. Go to the [API Library](https://console.cloud.google.com/apis/library)
2. Search for **"Generative Language API"** or **"Imagen API"**
3. Click on the API from the results
4. Click **"Enable"** button
5. Wait for the API to be enabled (this may take a minute)

## Step 4: Create API Credentials
1. Go to [Credentials page](https://console.cloud.google.com/apis/credentials)
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"API Key"** from the dropdown
4. Your API key will be generated and displayed
5. **IMPORTANT**: Copy the API key immediately (you won't be able to see it again)

## Step 5: Restrict Your API Key (Recommended for Security)
1. Click on the API key you just created to edit it
2. Under **"API restrictions"**, select **"Restrict key"**
3. Under **"Select APIs"**, choose **"Generative Language API"**
4. Under **"Application restrictions"**, select **"HTTP referrers (web sites)"**
5. Click **"Add an item"** and add your website URLs using the correct format:
   
   **For GitHub Pages:**
   - `https://rohithcz1982.github.io/*` (with wildcard for all paths)
   - `https://rohithcz1982.github.io/` (base URL)
   - `https://*.github.io/*` (if you want to allow all GitHub Pages sites - less secure)
   
   **For custom domains:**
   - `https://yourdomain.com/*` (with wildcard)
   - `https://yourdomain.com/` (base URL)
   
   **Important Notes:**
   - Always include the `https://` protocol
   - Use `/*` at the end to allow all paths on your domain
   - Don't include a trailing slash if you're using the wildcard `/*`
   - You can add multiple URLs (one per line)
   - For local testing, you can temporarily add: `http://localhost/*` or `http://127.0.0.1/*`
   
6. Click **"Save"**

## Step 6: Add API Key to Your Code
1. Open `postergenerator.html` in your code editor
2. Find the line with `const encodedApiKey = "";`
3. **Encode your API key** using one of these methods:
   - **Method 1 (Browser Console)**: Open browser console (F12) and run: `btoa("YOUR_API_KEY_HERE")`
   - **Method 2 (Online)**: Use a base64 encoder online
4. Replace the empty string with your encoded API key:
   ```javascript
   const encodedApiKey = "YOUR_ENCODED_API_KEY_HERE";
   ```
5. Save the file
   
   **Note**: The API key is encoded (not encrypted) for basic obfuscation. It can still be decoded by anyone viewing the code, but it's less obvious than plain text. For production, always restrict your API key in Google Cloud Console.

## Step 7: Set Up Billing (REQUIRED - Cannot Skip)
⚠️ **CRITICAL**: The Imagen API **REQUIRES** a billing account to be set up, even if you're using free credits. You will get an error "Imagen API is only accessible to billed users" without this step.

1. Go to [Billing](https://console.cloud.google.com/billing)
2. Click **"Link a billing account"** or **"Create billing account"**
3. Follow the prompts to set up billing (credit card required)
4. **Don't worry**: Google provides **$300 in free credits** for new accounts
5. You **won't be charged** until you exceed the free credits
6. Make sure to link the billing account to your project

## Pricing Information
- Check current pricing at: [Google Cloud Pricing](https://cloud.google.com/pricing)
- Imagen API pricing is typically per image generated
- Monitor your usage in the [Cloud Console](https://console.cloud.google.com/)

## Troubleshooting

### If you get "API not enabled" error:
- Make sure you've enabled the "Generative Language API" in Step 3
- Wait a few minutes after enabling for it to propagate

### If you get "Permission denied" or "are blocked" error:
- Check that your API key has the correct restrictions
- Make sure billing is enabled

### If you get "https://yourdomain.com/ are blocked" error:
This means your HTTP referrer restrictions are not configured correctly. Follow these steps:

1. **Go to Google Cloud Console** → [Credentials](https://console.cloud.google.com/apis/credentials)
2. **Click on your API key** to edit it
3. **Check the "Application restrictions"** section:
   - Make sure you selected **"HTTP referrers (web sites)"** (not "IP addresses" or "Android apps")
   - Verify the URL format is correct:
     - ✅ **Correct**: `https://rohithcz1982.github.io/*`
     - ✅ **Correct**: `https://rohithcz1982.github.io/`
     - ❌ **Wrong**: `rohithcz1982.github.io` (missing protocol)
     - ❌ **Wrong**: `https://rohithcz1982.github.io` (missing trailing wildcard or slash)
   
4. **For GitHub Pages specifically**, add BOTH of these:
   - `https://rohithcz1982.github.io/*`
   - `https://rohithcz1982.github.io/`
   
5. **Common issues:**
   - Missing `https://` protocol
   - Missing `/*` wildcard at the end
   - Extra spaces or typos in the URL
   - Using `http://` instead of `https://` (GitHub Pages uses HTTPS)
   
6. **After making changes**, wait 1-2 minutes for the changes to propagate
7. **Clear your browser cache** and try again
8. **For testing**, you can temporarily set restrictions to **"None"** to verify the API key works, then add restrictions back

### If you get "Imagen API is only accessible to billed users" error:
- **This means billing is not set up or not linked to your project**
- Go to [Billing](https://console.cloud.google.com/billing) and ensure:
  1. A billing account exists
  2. The billing account is linked to your project
  3. The project is selected in the billing account settings
- Wait a few minutes after linking for the changes to take effect
- Try generating again after billing is properly configured

## Security Best Practices
1. **Never commit your API key to public repositories**
2. **Use environment variables** for production (if using a backend)
3. **Restrict your API key** to specific APIs and domains
4. **Monitor usage** regularly in the Cloud Console
5. **Rotate keys** if you suspect they've been compromised

## Alternative: Using Environment Variables (Advanced)
For better security, you can store the API key in an environment variable instead of hardcoding it. However, since this is a client-side HTML file, you'll need a backend server to securely handle the API key.

---

**Note**: The Imagen API endpoint format may vary. If you encounter issues, check the [Google AI Studio](https://aistudio.google.com/) or [Google Cloud Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview) for the latest API endpoint format.

