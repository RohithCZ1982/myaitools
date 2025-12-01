// Vercel Serverless Function to proxy Google Imagen API requests
// This keeps your API key secure on the server side

export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Get API key from environment variable
  const apiKey = process.env.GOOGLE_IMAGEN_API_KEY;

  if (!apiKey) {
    console.error('API key not configured');
    return res.status(500).json({ 
      error: 'Server configuration error: API key not set' 
    });
  }

  try {
    // Get the request body from the client
    const { prompt, aspectRatio = '9:16', sampleCount = 1 } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    // Construct the API URL with the server-side API key
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key=${apiKey}`;

    // Prepare the payload for Google Imagen API
    const payload = {
      instances: [{ 
        prompt: prompt
      }],
      parameters: {
        sampleCount: sampleCount,
        aspectRatio: aspectRatio
      }
    };

    // Make the request to Google Imagen API
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('Google API Error:', data);
      return res.status(response.status).json({ 
        error: data.error?.message || 'Failed to generate image',
        details: data
      });
    }

    // Return the response to the client
    return res.status(200).json(data);

  } catch (error) {
    console.error('Proxy Error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
}

