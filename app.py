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
import httpx

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
    address: Optional[str] = None  # Physical address (computed from coordinates)
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
async def create_clock_record(record: ClockRecord):
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
        
        # Optionally get address if coordinates exist
        address = None
        if row[4] is not None and row[5] is not None:
            try:
                geocode_result = await reverse_geocode_coords(row[4], row[5])
                address = geocode_result.get("address", None)
            except Exception:
                address = None
        
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
            address=address,
            created_at=str(row[9] if len(row) > 9 else row[8])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clock", response_model=List[ClockRecordResponse])
async def get_clock_records(worker_name: Optional[str] = None, limit: int = 100, include_address: bool = False):
    """Get clock records, optionally filtered by worker name. Set include_address=True to get physical addresses."""
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
            address = None
            # If include_address is True and we have coordinates, get the address
            if include_address and row[4] is not None and row[5] is not None:
                try:
                    geocode_result = await reverse_geocode_coords(row[4], row[5])
                    address = geocode_result.get("address", None)
                except Exception as e:
                    # If geocoding fails, just leave address as None
                    address = None
            
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
                address=address,
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

@app.delete("/api/clock/{record_id}")
def delete_clock_record(record_id: int):
    """Delete a clock record by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if record exists
        if USE_POSTGRES:
            cursor.execute("SELECT id FROM clock_records WHERE id = %s", (record_id,))
        else:
            cursor.execute("SELECT id FROM clock_records WHERE id = ?", (record_id,))
        
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Delete the record
        if USE_POSTGRES:
            cursor.execute("DELETE FROM clock_records WHERE id = %s", (record_id,))
        else:
            cursor.execute("DELETE FROM clock_records WHERE id = ?", (record_id,))
        
        conn.commit()
        conn.close()
        
        return {"message": "Record deleted successfully", "id": record_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class BulkDeleteRequest(BaseModel):
    record_ids: List[int]

@app.delete("/api/clock/bulk")
def delete_clock_records_bulk(request: BulkDeleteRequest):
    """Delete multiple clock records by IDs"""
    try:
        record_ids = request.record_ids
        if not record_ids or len(record_ids) == 0:
            raise HTTPException(status_code=400, detail="No record IDs provided")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        deleted_count = 0
        
        for record_id in record_ids:
            try:
                if USE_POSTGRES:
                    cursor.execute("DELETE FROM clock_records WHERE id = %s", (record_id,))
                else:
                    cursor.execute("DELETE FROM clock_records WHERE id = ?", (record_id,))
                deleted_count += cursor.rowcount
            except Exception as e:
                print(f"Error deleting record {record_id}: {e}")
                continue  # Skip if record doesn't exist
        
        conn.commit()
        conn.close()
        
        return {"message": f"Deleted {deleted_count} record(s) successfully", "deleted_count": deleted_count}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in bulk delete: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete records: {str(e)}")

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

async def reverse_geocode_with_google(latitude: float, longitude: float, api_key: str):
    """Convert GPS coordinates to address using Google Geocoding API (more accurate)"""
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{latitude},{longitude}",
            "key": api_key,
            "result_type": "street_address|postal_code"  # Prioritize street addresses and postal codes
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "OK" or not data.get("results"):
            return None
        
        # Get the first result (most specific)
        result = data["results"][0]
        address_components = result.get("address_components", [])
        
        # Extract address parts
        address_parts = {}
        postcode = None
        
        for component in address_components:
            types = component.get("types", [])
            long_name = component.get("long_name", "")
            
            if "street_number" in types:
                address_parts["house_number"] = long_name
            elif "route" in types:
                address_parts["road"] = long_name
            elif "locality" in types or "sublocality" in types:
                address_parts["city"] = long_name
            elif "administrative_area_level_1" in types:
                address_parts["state"] = long_name
            elif "postal_code" in types:
                postcode = long_name
            elif "country" in types:
                address_parts["country"] = long_name
        
        # Build formatted address
        address_components_list = []
        if address_parts.get("house_number"):
            address_components_list.append(address_parts["house_number"])
        if address_parts.get("road"):
            address_components_list.append(address_parts["road"])
        if address_parts.get("city"):
            address_components_list.append(address_parts["city"])
        if address_parts.get("state"):
            address_components_list.append(address_parts["state"])
        if postcode:
            address_components_list.append(postcode)
        if address_parts.get("country"):
            address_components_list.append(address_parts["country"])
        
        formatted_address = ", ".join(address_components_list) if address_components_list else result.get("formatted_address", "")
        
        return {
            "address": formatted_address,
            "coordinates": f"{latitude}, {longitude}",
            "raw": result.get("formatted_address", ""),
            "postcode": postcode
        }
    except Exception as e:
        print(f"Google Geocoding error: {e}")
        return None

async def reverse_geocode_coords(latitude: float, longitude: float):
    """Convert GPS coordinates to physical address using OpenStreetMap Nominatim (with Google fallback)"""
    # Try OpenStreetMap first (free)
    try:
        # Use OpenStreetMap Nominatim API (free, no API key required)
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "addressdetails": 1,
            "zoom": 18,  # Higher zoom for more detailed address
            "namedetails": 1  # Include named details for better accuracy
        }
        headers = {
            "User-Agent": "WorkersClockApp/1.0"  # Required by Nominatim usage policy
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        
        if "error" in data:
            raise Exception("OpenStreetMap returned error")
        
        # Extract address components
        address_parts = data.get("address", {})
        address_components = []
        
        # Build address from most specific to least specific
        if address_parts.get("house_number"):
            address_components.append(address_parts["house_number"])
        if address_parts.get("road"):
            address_components.append(address_parts["road"])
        if address_parts.get("suburb") or address_parts.get("neighbourhood"):
            address_components.append(address_parts.get("suburb") or address_parts.get("neighbourhood"))
        if address_parts.get("city") or address_parts.get("town") or address_parts.get("village"):
            address_components.append(address_parts.get("city") or address_parts.get("town") or address_parts.get("village"))
        if address_parts.get("state"):
            address_components.append(address_parts["state"])
        
        # Try multiple postcode field names (different regions use different names)
        postcode = (
            address_parts.get("postcode") or 
            address_parts.get("postal_code") or 
            address_parts.get("postalcode") or
            address_parts.get("zip") or
            address_parts.get("zipcode")
        )
        if postcode:
            address_components.append(postcode)
        
        if address_parts.get("country"):
            address_components.append(address_parts["country"])
        
        # If we have components, join them; otherwise use display_name
        if address_components:
            formatted_address = ", ".join(address_components)
        else:
            display_name = data.get("display_name", "")
            # Only use display_name if it looks like a real address (not just coordinates)
            if display_name and len(display_name) > 20 and "," in display_name:
                formatted_address = display_name
            else:
                # If no proper address found, return None to avoid showing coordinates twice
                formatted_address = None
        
        # If postcode is missing or seems wrong, try Google as fallback
        google_api_key = os.getenv("GOOGLE_GEOCODING_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if (not postcode or len(str(postcode)) < 4) and google_api_key:
            # Try Google Geocoding for better postcode accuracy
            google_result = await reverse_geocode_with_google(latitude, longitude, google_api_key)
            if google_result:
                # If we got a full address from Google, use it
                if google_result.get("address"):
                    formatted_address = google_result["address"]
                # Use Google's postcode if available
                if google_result.get("postcode"):
                    postcode = google_result["postcode"]
                    # Update address with correct postcode if we have an address
                    if formatted_address and postcode not in formatted_address:
                        # Replace old postcode or add new one
                        import re
                        formatted_address = re.sub(r'\b\d{4,6}\b', postcode, formatted_address)
                        if postcode not in formatted_address:
                            # Insert postcode before country
                            parts = formatted_address.split(", ")
                            if address_parts.get("country") and address_parts["country"] in parts:
                                idx = parts.index(address_parts["country"])
                                parts.insert(idx, postcode)
                            else:
                                parts.append(postcode)
                            formatted_address = ", ".join(parts)
        
        # Also return postcode separately for verification
        return {
            "address": formatted_address,
            "coordinates": f"{latitude}, {longitude}",
            "raw": data.get("display_name", ""),
            "postcode": postcode  # Return postcode separately
        }
        
    except (httpx.TimeoutException, Exception) as e:
        # Fallback to Google Geocoding if OpenStreetMap fails
        google_api_key = os.getenv("GOOGLE_GEOCODING_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            google_result = await reverse_geocode_with_google(latitude, longitude, google_api_key)
            if google_result:
                return google_result
        
        # If both fail, return None for address (don't duplicate coordinates)
        print(f"Geocoding failed: {e}")
        return {
            "address": None,  # Return None instead of coordinates to avoid duplication
            "coordinates": f"{latitude}, {longitude}",
            "postcode": None
        }

class SQLQueryRequest(BaseModel):
    query: str
    allow_write: bool = False  # Allow INSERT, UPDATE, DELETE operations

@app.post("/api/sql/execute")
async def execute_sql_query(request: SQLQueryRequest):
    """Execute SQL query with safety checks"""
    try:
        query = request.query.strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Security: Block dangerous operations
        dangerous_keywords = ['DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE']
        query_upper = query.upper()
        
        # Check for dangerous operations
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Operation '{keyword}' is not allowed for security reasons"
                )
        
        # If write operations not allowed, block INSERT, UPDATE, DELETE
        if not request.allow_write:
            write_keywords = ['INSERT', 'UPDATE', 'DELETE']
            for keyword in write_keywords:
                if keyword in query_upper:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Write operations are disabled. Enable 'Allow Write Operations' to execute {keyword} statements."
                    )
        
        # Limit query execution time and result size
        conn = get_db_connection()
        cursor = conn.cursor()
        
        import time
        start_time = time.time()
        
        try:
            # Execute query
            cursor.execute(query)
            
            # Check if it's a SELECT query (returns rows)
            if query_upper.strip().startswith('SELECT'):
                rows = cursor.fetchall()
                
                # Get column names
                if USE_POSTGRES:
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                else:
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Limit results to 1000 rows
                if len(rows) > 1000:
                    rows = rows[:1000]
                    warning = f"Results limited to 1000 rows. Total rows: {len(rows)}"
                else:
                    warning = None
                
                execution_time = time.time() - start_time
                
                # Convert rows to list of dicts for JSON serialization
                result_rows = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        # Handle different data types
                        value = row[i]
                        if value is None:
                            row_dict[col] = None
                        elif isinstance(value, (int, float, str, bool)):
                            row_dict[col] = value
                        else:
                            # Convert other types to string
                            row_dict[col] = str(value)
                    result_rows.append(row_dict)
                
                conn.close()
                
                return {
                    "success": True,
                    "columns": columns,
                    "rows": result_rows,
                    "row_count": len(result_rows),
                    "execution_time_ms": round(execution_time * 1000, 2),
                    "warning": warning
                }
            else:
                # For non-SELECT queries (INSERT, UPDATE, DELETE)
                conn.commit()
                rows_affected = cursor.rowcount
                execution_time = time.time() - start_time
                conn.close()
                
                return {
                    "success": True,
                    "message": f"Query executed successfully. Rows affected: {rows_affected}",
                    "rows_affected": rows_affected,
                    "execution_time_ms": round(execution_time * 1000, 2)
                }
                
        except Exception as db_error:
            conn.rollback()
            conn.close()
            raise HTTPException(status_code=400, detail=f"SQL Error: {str(db_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")

@app.get("/api/sql/tables")
async def get_table_list():
    """Get list of all tables in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
        else:
            cursor.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
        
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tables: {str(e)}")

@app.get("/api/sql/table/{table_name}")
async def get_table_schema(table_name: str):
    """Get schema information for a specific table"""
    try:
        # Sanitize table name (prevent SQL injection)
        if not table_name.replace('_', '').replace('-', '').isalnum():
            raise HTTPException(status_code=400, detail="Invalid table name")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
        else:
            cursor.execute(f"PRAGMA table_info({table_name})")
        
        columns = cursor.fetchall()
        conn.close()
        
        if USE_POSTGRES:
            schema = [
                {
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2] == "YES",
                    "default": col[3]
                }
                for col in columns
            ]
        else:
            schema = [
                {
                    "name": col[1],
                    "type": col[2],
                    "nullable": col[3] == 0,
                    "default": col[4]
                }
                for col in columns
            ]
        
        return {"table": table_name, "schema": schema}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching table schema: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

