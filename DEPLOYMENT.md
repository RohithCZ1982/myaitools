# Deployment Guide for Workers Clock In/Out API

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python app.py
   ```
   Or:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Update frontend API URL:**
   In `workerclock.html`, set:
   ```javascript
   const BACKEND_API_URL = 'http://localhost:8000';
   ```

## Deploy to Render

### Step 1: Prepare Your Repository

1. Make sure all files are committed to Git:
   - `app.py`
   - `requirements.txt`
   - `render.yaml` (optional, but recommended)

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Connect your GitHub/GitLab repository

### Step 3: Create New Web Service

1. Click "New +" → "Web Service"
2. Connect your repository
3. Configure the service:
   - **Name:** `worker-clock-api` (or your preferred name)
   - **Environment:** `Python 3`
   - **Build Command:** `mkdir -p /tmp/cargo && pip install --upgrade pip setuptools wheel && pip install --prefer-binary --no-cache-dir -r requirements.txt`
   - **Environment Variables:**
     - `CARGO_HOME=/tmp/cargo` (allows Rust/Cargo to use writable directory)
     - `PYTHON_VERSION=3.11.0`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free tier is fine for testing

### Step 4: Environment Variables (Optional)

If you want to use PostgreSQL instead of SQLite:

1. Add a PostgreSQL database in Render
2. Add environment variables:
   - `DATABASE_URL` (provided by Render for PostgreSQL)

### Step 5: Update Frontend

1. Once deployed, copy your Render URL (e.g., `https://worker-clock-api.onrender.com`)
2. Update `workerclock.html`:
   ```javascript
   const BACKEND_API_URL = 'https://your-app-name.onrender.com';
   ```

### Step 6: Test

1. Visit your Render service URL
2. You should see: `{"message": "Workers Clock In/Out API", "status": "running"}`
3. Test the clock in/out functionality from your frontend

## Database Options

### SQLite (Default - Free)
- Works out of the box
- Data persists in the file system
- Good for small to medium deployments
- **Note:** On Render free tier, filesystem is ephemeral (data may be lost on restart)

### PostgreSQL (Recommended for Production)
1. Create a PostgreSQL database in Render
2. Update `app.py` to use PostgreSQL instead of SQLite
3. Install `psycopg2` or `asyncpg` in requirements.txt

## API Endpoints

- `GET /` - Health check
- `POST /api/clock` - Save clock in/out record
- `GET /api/clock` - Get all clock records (optional: `?worker_name=John&limit=100`)
- `GET /api/clock/stats` - Get statistics (optional: `?worker_name=John`)

## Troubleshooting

1. **CORS Errors:** Make sure CORS middleware is configured in `app.py`
2. **Database Issues:** Check that the database file has write permissions
3. **Port Issues:** Render uses `$PORT` environment variable automatically
4. **Build Failures:** Check that all dependencies are in `requirements.txt`

## Notes

- Free tier on Render spins down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Consider upgrading to paid tier for always-on service
- For production, use PostgreSQL instead of SQLite

