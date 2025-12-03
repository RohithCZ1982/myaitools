# Image Encryption Setup Guide

## Overview

All check-in/check-out images are automatically encrypted before storage in the database using AES-256 encryption (Fernet symmetric encryption).

## Security Features

1. **Automatic Encryption**: Images are encrypted on the server before storage
2. **Secure Key Management**: Uses environment variable for encryption key
3. **Base64 Encoding**: Encrypted data is stored as base64 strings in database
4. **Decryption Endpoint**: Secure endpoint to retrieve decrypted images when needed

## Setup

### 1. Generate Encryption Key

```python
from cryptography.fernet import Fernet

# Generate a new key
key = Fernet.generate_key()
print(key.decode())  # Copy this value
```

### 2. Set Environment Variable

**For Local Development:**
```bash
export ENCRYPTION_KEY="your-generated-key-here"
```

**For Render Deployment:**
1. Go to your Render service dashboard
2. Navigate to "Environment" tab
3. Add new environment variable:
   - Key: `ENCRYPTION_KEY`
   - Value: Your generated key (from step 1)

### 3. Important Notes

⚠️ **CRITICAL**: 
- **Never commit the encryption key to Git**
- **Keep the key secure and backed up**
- **If you lose the key, encrypted images cannot be decrypted**
- **Use different keys for development and production**

## API Endpoints

### Save Record with Encrypted Image
```
POST /api/clock
Body: {
    "worker_name": "John Doe",
    "action": "check-in",
    "timestamp": "2024-01-15T10:30:00Z",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "image_data": "data:image/jpeg;base64,/9j/4AAQ..." // Base64 image
}
```

### Retrieve Decrypted Image
```
GET /api/clock/{record_id}/image
Response: {
    "image": "data:image/jpeg;base64,...",
    "record_id": 123
}
```

## Database Schema

The `clock_records` table includes:
- `encrypted_image` (TEXT): Base64-encoded encrypted image data

## How It Works

1. **Frontend** sends base64 image data in `image_data` field
2. **Backend** receives image and encrypts it using Fernet cipher
3. **Encrypted data** is stored in database as base64 string
4. **Decryption** happens only when explicitly requested via API endpoint

## Security Best Practices

1. ✅ Images are encrypted at rest in database
2. ✅ Encryption key stored in environment variable (not in code)
3. ✅ HTTPS should be used in production (Render provides this)
4. ✅ Access control should be added to decryption endpoint in production
5. ✅ Consider adding authentication/authorization for image retrieval

## Troubleshooting

### "Encryption failed" error
- Check that `ENCRYPTION_KEY` is set correctly
- Ensure the key is valid Fernet key format
- Check server logs for detailed error messages

### "Decryption failed" error
- Verify the encryption key matches the one used for encryption
- Check that the encrypted data wasn't corrupted
- Ensure the record exists in database

### Key Rotation
If you need to rotate encryption keys:
1. Decrypt all existing images with old key
2. Re-encrypt with new key
3. Update `ENCRYPTION_KEY` environment variable
4. This requires a migration script (not included)

## Example: Generate Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and use it as your `ENCRYPTION_KEY` environment variable.

