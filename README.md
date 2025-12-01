# AI Poster Generator

A beautiful, AI-powered poster generator for creating stunning social media posters (Instagram Stories, WhatsApp Status) with a 9:16 vertical aspect ratio.

## Features

- 🎨 AI-powered poster generation
- 📱 Perfect 9:16 aspect ratio for social media
- 🖼️ Logo upload support
- 🎯 Customizable themes and styles
- 📥 Download generated posters
- 💻 Modern, responsive UI

## Quick Start

1. **Set up your API key**:
   - Follow instructions in [API_KEY_SETUP.md](./API_KEY_SETUP.md)
   - Add your Google Imagen API key in `postergenerator.html` (line 167)

2. **Set up billing** (Required):
   - Google Cloud requires billing to be enabled
   - New accounts get $300 in free credits
   - See [API_KEY_SETUP.md](./API_KEY_SETUP.md) for details

3. **Open the application**:
   - Open `index.html` in your browser
   - Click "Call Poster Generator"
   - Fill in the form and generate!

## Files

- `index.html` - Landing page
- `postergenerator.html` - Main poster generator application
- `poster-generator.html` - Redirect page to Gemini (optional)
- `API_KEY_SETUP.md` - Detailed API key setup instructions
- `DEPLOYMENT_GUIDE.md` - Guide for sharing/deploying the application

## Sharing with Others

**⚠️ Important Security Note**: The API key is visible in the code. Before sharing:

1. **Restrict your API key** in Google Cloud Console:
   - Set HTTP referrer restrictions to your domain
   - Limit to only "Generative Language API"
   - Monitor usage regularly

2. **Set up billing alerts** to avoid unexpected charges

3. **Consider using a backend** for production use (see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md))

For detailed deployment options, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).

## Deployment Options

- **GitHub Pages** (Free, easy)
- **Netlify** (Free, drag & drop)
- **Vercel** (Free, automatic)
- **Backend proxy** (Most secure, requires server)

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for step-by-step instructions.

## Troubleshooting

### "API Key Required" error
- Make sure you've added your API key in `postergenerator.html` (line 167)
- Save the file and refresh your browser

### "Billing account required" error
- Set up billing in [Google Cloud Console](https://console.cloud.google.com/billing)
- Link billing account to your project
- Wait a few minutes for changes to take effect

### Other errors
- Check the browser console (F12) for detailed error messages
- See [API_KEY_SETUP.md](./API_KEY_SETUP.md) for troubleshooting

## Cost Management

- Google provides $300 free credits for new accounts
- Set up billing alerts in Google Cloud Console
- Monitor API usage regularly
- Set daily/monthly usage limits

## License

This project is open source. Use at your own risk regarding API costs.

## Support

For issues or questions:
- Check [API_KEY_SETUP.md](./API_KEY_SETUP.md) for API setup
- Check [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for deployment
- Review Google Cloud documentation for API details

