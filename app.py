from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os
import base64
from typing import List, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

app = FastAPI(title="Workers Clock In/Out API")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup - supports both SQLite (local) and PostgreSQL (production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///worker_clock.db")
USE_POSTGRES = DATABASE_URL.startswith("postgres")

# Encryption setup
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", None)
if not ENCRYPTION_KEY:
    # Generate a key if not provided (for development only)
    # In production, set ENCRYPTION_KEY environment variable
    key = Fernet.generate_key()
    ENCRYPTION_KEY = key.decode()
    print(f"WARNING: Using auto-generated encryption key. Set ENCRYPTION_KEY env var for production!")

# Initialize Fernet cipher
try:
    cipher = Fernet(ENCRYPTION_KEY.encode())
except Exception as e:
    print(f"Error initializing encryption: {e}")
    # Generate new key if provided key is invalid
    key = Fernet.generate_key()
    cipher = Fernet(key)
    ENCRYPTION_KEY = key.decode()
    print("Generated new encryption key")

def encrypt_image(image_data: str) -> str:
    """Encrypt base64 image data"""
    try:
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        # Encrypt
        encrypted_data = cipher.encrypt(image_bytes)
        # Encode back to base64 for storage
        return base64.b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        raise Exception(f"Encryption failed: {str(e)}")

def decrypt_image(encrypted_data: str) -> str:
    """Decrypt image data and return base64 string"""
    try:
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        # Decrypt
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        # Encode back to base64 for frontend
        return base64.b64encode(decrypted_bytes).decode('utf-8')
    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")

def get_db_connection():
    """Get database connection - SQLite for local, PostgreSQL for production"""
    global USE_POSTGRES
    if USE_POSTGRES:
        try:
            import psycopg2
            from urllib.parse import urlparse
            result = urlparse(DATABASE_URL)
            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
            return conn
        except ImportError:
            print("PostgreSQL detected but psycopg2 not installed. Using SQLite fallback.")
            USE_POSTGRES = False
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}. Using SQLite fallback.")
            USE_POSTGRES = False
    
    # Fallback to SQLite
    return sqlite3.connect("worker_clock.db")

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clock_records (
                id SERIAL PRIMARY KEY,
                worker_name TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                accuracy REAL,
                face_data TEXT,
                encrypted_image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Add encrypted_image column if it doesn't exist (for existing databases)
        try:
            cursor.execute("""
                ALTER TABLE clock_records 
                ADD COLUMN IF NOT EXISTS encrypted_image TEXT
            """)
        except Exception:
            pass  # Column already exists
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clock_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_name TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                accuracy REAL,
                face_data TEXT,
                encrypted_image TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Add encrypted_image column if it doesn't exist (for existing databases)
        try:
            cursor.execute("PRAGMA table_info(clock_records)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'encrypted_image' not in columns:
                cursor.execute("""
                    ALTER TABLE clock_records 
                    ADD COLUMN encrypted_image TEXT
                """)
        except Exception:
            pass  # Column already exists or table doesn't exist yet
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Mount static files directory to serve HTML files
# This allows accessing files like /index.html, /workerclock.html, etc.
app.mount("/static", StaticFiles(directory="."), name="static")

# Pydantic models for request/response
class ClockRecord(BaseModel):
    worker_name: str
    action: str  # "check-in" or "check-out"
    timestamp: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    face_data: Optional[str] = None
    image_data: Optional[str] = None  # Base64 image data (will be encrypted before storage)

class ClockRecordResponse(BaseModel):
    id: int
    worker_name: str
    action: str
    timestamp: str
    latitude: Optional[float]
    longitude: Optional[float]
    accuracy: Optional[float]
    face_data: Optional[str]
    encrypted_image: Optional[str] = None  # Encrypted image (not decrypted in response by default)
    created_at: str

@app.get("/")
def read_root():
    """Serve index.html at the root URL"""
    try:
        return FileResponse("index.html")
    except FileNotFoundError:
        return {"message": "Workers Clock In/Out API", "status": "running", "index.html": "not found"}

@app.get("/api")
def api_info():
    """API information endpoint"""
    return {"message": "Workers Clock In/Out API", "status": "running"}

# Serve JavaScript files from root
@app.get("/{filename}.js")
def serve_js(filename: str):
    """Serve JavaScript files like /config.js, etc."""
    # Don't serve files from api/ subdirectory via this route
    if filename.startswith("api/"):
        raise HTTPException(status_code=404, detail="File not found")
    js_file = f"{filename}.js"
    if os.path.exists(js_file):
        return FileResponse(js_file, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="File not found")

# Serve JavaScript files from api subdirectory
@app.get("/api/{filename}.js")
def serve_api_js(filename: str):
    """Serve JavaScript files from api/ directory"""
    js_file = f"api/{filename}.js"
    if os.path.exists(js_file):
        return FileResponse(js_file, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="File not found")

# Serve HTML files directly
@app.get("/{filename}.html")
def serve_html(filename: str):
    """Serve HTML files like /workerclock.html, /admin.html, etc."""
    html_file = f"{filename}.html"
    if os.path.exists(html_file):
        return FileResponse(html_file)
    raise HTTPException(status_code=404, detail="File not found")

# Serve image files
@app.get("/{filename}.jpg")
def serve_jpg(filename: str):
    """Serve JPG images"""
    img_file = f"{filename}.jpg"
    if os.path.exists(img_file):
        return FileResponse(img_file, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/{filename}.png")
def serve_png(filename: str):
    """Serve PNG images"""
    img_file = f"{filename}.png"
    if os.path.exists(img_file):
        return FileResponse(img_file, media_type="image/png")
    raise HTTPException(status_code=404, detail="File not found")

# Serve CSS files
@app.get("/{filename}.css")
def serve_css(filename: str):
    """Serve CSS files"""
    css_file = f"{filename}.css"
    if os.path.exists(css_file):
        return FileResponse(css_file, media_type="text/css")
    raise HTTPException(status_code=404, detail="File not found")

@app.post("/api/clock", response_model=ClockRecordResponse)
def create_clock_record(record: ClockRecord):
    """Save a clock in/out record with encrypted image"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Encrypt image if provided
        encrypted_image = None
        if record.image_data:
            try:
                encrypted_image = encrypt_image(record.image_data)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Image encryption failed: {str(e)}")
        
        if USE_POSTGRES:
            cursor.execute("""
                INSERT INTO clock_records 
                (worker_name, action, timestamp, latitude, longitude, accuracy, face_data, encrypted_image)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                record.worker_name,
                record.action,
                record.timestamp,
                record.latitude,
                record.longitude,
                record.accuracy,
                record.face_data,
                encrypted_image
            ))
            record_id = cursor.fetchone()[0]
        else:
            cursor.execute("""
                INSERT INTO clock_records 
                (worker_name, action, timestamp, latitude, longitude, accuracy, face_data, encrypted_image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.worker_name,
                record.action,
                record.timestamp,
                record.latitude,
                record.longitude,
                record.accuracy,
                record.face_data,
                encrypted_image
            ))
            record_id = cursor.lastrowid
        
        conn.commit()
        
        # Fetch the created record
        if USE_POSTGRES:
            cursor.execute("SELECT * FROM clock_records WHERE id = %s", (record_id,))
        else:
            cursor.execute("SELECT * FROM clock_records WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        conn.close()
        
        return ClockRecordResponse(
            id=row[0],
            worker_name=row[1],
            action=row[2],
            timestamp=row[3],
            latitude=row[4],
            longitude=row[5],
            accuracy=row[6],
            face_data=row[7],
            encrypted_image=row[8] if len(row) > 8 else None,
            created_at=str(row[9] if len(row) > 9 else row[8])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clock", response_model=List[ClockRecordResponse])
def get_clock_records(worker_name: Optional[str] = None, limit: int = 100):
    """Get clock records, optionally filtered by worker name"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if worker_name:
            if USE_POSTGRES:
                cursor.execute("""
                    SELECT * FROM clock_records 
                    WHERE worker_name = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (worker_name, limit))
            else:
                cursor.execute("""
                    SELECT * FROM clock_records 
                    WHERE worker_name = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (worker_name, limit))
        else:
            if USE_POSTGRES:
                cursor.execute("""
                    SELECT * FROM clock_records 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
            else:
                cursor.execute("""
                    SELECT * FROM clock_records 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            records.append(ClockRecordResponse(
                id=row[0],
                worker_name=row[1],
                action=row[2],
                timestamp=row[3],
                latitude=row[4],
                longitude=row[5],
                accuracy=row[6],
                face_data=row[7],
                encrypted_image=row[8] if len(row) > 8 else None,
                created_at=str(row[9] if len(row) > 9 else row[8])
            ))
        
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clock/stats")
def get_clock_stats(worker_name: Optional[str] = None):
    """Get statistics about clock records"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if worker_name:
            if USE_POSTGRES:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        SUM(CASE WHEN action = 'check-in' THEN 1 ELSE 0 END) as check_ins,
                        SUM(CASE WHEN action = 'check-out' THEN 1 ELSE 0 END) as check_outs
                    FROM clock_records 
                    WHERE worker_name = %s
                """, (worker_name,))
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        SUM(CASE WHEN action = 'check-in' THEN 1 ELSE 0 END) as check_ins,
                        SUM(CASE WHEN action = 'check-out' THEN 1 ELSE 0 END) as check_outs
                    FROM clock_records 
                    WHERE worker_name = ?
                """, (worker_name,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    SUM(CASE WHEN action = 'check-in' THEN 1 ELSE 0 END) as check_ins,
                    SUM(CASE WHEN action = 'check-out' THEN 1 ELSE 0 END) as check_outs
                FROM clock_records
            """)
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total_records": row[0] or 0,
            "check_ins": row[1] or 0,
            "check_outs": row[2] or 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clock/{record_id}/image")
def get_decrypted_image(record_id: int):
    """Get decrypted image for a specific record (for viewing)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute("SELECT encrypted_image FROM clock_records WHERE id = %s", (record_id,))
        else:
            cursor.execute("SELECT encrypted_image FROM clock_records WHERE id = ?", (record_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail="Image not found")
        
        try:
            decrypted_base64 = decrypt_image(row[0])
            return {
                "image": f"data:image/jpeg;base64,{decrypted_base64}",
                "record_id": record_id
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

