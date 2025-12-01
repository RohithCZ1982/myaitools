# Deployment Guide - Sharing Your Poster Generator

This guide explains how to share your AI Poster Generator with others while keeping your API key secure.

## ⚠️ Security Warning

**IMPORTANT**: Your API key is currently visible in the HTML file. If you share this file directly, anyone can see and use your API key, which could:
- Lead to unexpected charges on your Google Cloud account
- Exceed your usage limits
- Compromise your account security

## Option 1: Free Static Hosting (Recommended for Testing)

### GitHub Pages (Free)

1. **Create a GitHub account** (if you don't have one)
2. **Create a new repository**:
   - Go to [GitHub](https://github.com)
   - Click "New repository"
   - Name it (e.g., "ai-poster-generator")
   - Make it **Public** (required for free GitHub Pages)
   - Don't initialize with README

3. **Upload your files**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ai-poster-generator.git
   git push -u origin main
   ```

4. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Select "main" branch
   - Click Save
   - Your site will be at: `https://YOUR_USERNAME.github.io/ai-poster-generator/`

5. **⚠️ Security Note**: Since the API key is in the HTML, anyone can view it. Consider Option 2 for production.

### Netlify (Free)

1. Go to [Netlify](https://www.netlify.com)
2. Sign up/login
3. Drag and drop your project folder, OR
4. Connect to GitHub for automatic deployments
5. Your site will be live at: `https://your-site-name.netlify.app`

### Vercel (Free)

1. Go to [Vercel](https://vercel.com)
2. Sign up/login
3. Import your project from GitHub or upload files
4. Deploy - your site will be live instantly

## Option 2: Secure Deployment (Recommended for Production)

### Using Environment Variables (Requires Backend)

For production use, you should use a backend to hide your API key:

1. **Create a simple backend** (Node.js example):
   ```javascript
   // server.js
   const express = require('express');
   const app = express();
   app.use(express.json());
   app.use(express.static('public'));

   app.post('/api/generate', async (req, res) => {
       const { prompt } = req.body;
       const apiKey = process.env.GOOGLE_API_KEY; // From environment variable
       
       // Make API call server-side
       const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key=${apiKey}`, {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({
               instances: [{ prompt }],
               parameters: { sampleCount: 1, aspectRatio: "9:16" }
           })
       });
       
       const data = await response.json();
       res.json(data);
   });

   app.listen(3000);
   ```

2. **Deploy backend** to services like:
   - [Railway](https://railway.app) (Free tier available)
   - [Render](https://render.com) (Free tier available)
   - [Heroku](https://heroku.com) (Paid)
   - [Google Cloud Run](https://cloud.google.com/run) (Pay as you go)

3. **Update frontend** to call your backend instead of Google API directly

## Option 3: API Key Restrictions (Partial Security)

If you must use the frontend-only approach, restrict your API key:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Click on your API key
3. Under **"Application restrictions"**:
   - Select **"HTTP referrers (web sites)"**
   - Add your deployed domain (e.g., `https://your-site.netlify.app/*`)
4. Under **"API restrictions"**:
   - Select **"Restrict key"**
   - Choose only **"Generative Language API"**
5. Click **Save**

This limits where the key can be used, but it's still visible in the code.

## Option 4: Share Locally (For Testing)

### Using Python Simple Server

1. Open terminal in your project folder
2. Run:
   ```bash
   # Python 3
   python -m http.server 8000
   
   # Python 2
   python -m SimpleHTTPServer 8000
   ```
3. Share your local IP address: `http://YOUR_IP:8000`
4. Others on your network can access it

### Using Node.js http-server

1. Install: `npm install -g http-server`
2. Run: `http-server -p 8000`
3. Share: `http://YOUR_IP:8000`

## Option 5: Cloud Storage (Google Cloud Storage / AWS S3)

1. Upload files to cloud storage bucket
2. Enable static website hosting
3. Make bucket public
4. Share the URL

## Best Practices for Sharing

1. **Monitor Usage**: Set up billing alerts in Google Cloud Console
2. **Set Quotas**: Limit API usage to prevent unexpected charges
3. **Use API Key Restrictions**: Always restrict your API key to specific domains
4. **Rate Limiting**: Consider adding rate limiting if many users will access it
5. **Terms of Service**: Add a terms page explaining usage limits

## Quick Deploy Checklist

- [ ] Remove any sensitive data from code
- [ ] Test the application locally
- [ ] Set up API key restrictions
- [ ] Choose hosting platform
- [ ] Deploy files
- [ ] Test deployed version
- [ ] Set up billing alerts
- [ ] Share the URL with users

## Cost Management

1. **Set Budget Alerts**:
   - Go to [Google Cloud Billing](https://console.cloud.google.com/billing)
   - Set up budget alerts
   - Get notified before reaching limits

2. **Monitor Usage**:
   - Check API usage regularly
   - Set daily/monthly limits

3. **Free Tier**:
   - Google provides $300 free credits
   - Monitor usage to stay within free tier

## Need Help?

- Check the [API_KEY_SETUP.md](./API_KEY_SETUP.md) for API setup
- Review Google Cloud documentation for API restrictions
- Consider using a backend service for better security

