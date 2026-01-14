from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, json, uuid, sys

app = Flask(__name__)
CORS(app)

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    DATA_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = BASE_DIR

DB_PATH = os.path.join(DATA_DIR, 'db.json')
MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
IMAGES_DIR = os.path.join(MEDIA_ROOT, 'images')
VIDEOS_DIR = os.path.join(MEDIA_ROOT, 'videos')

DEFAULT = {
    "items": [],
    "favorites": [],
    "user": None,
    "users": [{"email": "admin@niro.com", "name": "Administrador", "role": "admin", "password": "admin123", "banned": False}],
    "codes": [],
    "pendingVerifyEmail": None,
    "notifications": []
}

def read_db():
    if not os.path.exists(DB_PATH):
        return DEFAULT
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT

def write_db(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.get('/db')
def get_db():
    return jsonify(read_db())

@app.route('/')
def index():
    # SERVING index.html (Main App)
    response = send_from_directory(BASE_DIR, 'index.html')
    # FORCE NO CACHE
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/<path:path>')
def serve_static(path):
    response = send_from_directory(BASE_DIR, path)
    static_ext = ('.js', '.css', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.webp')
    if any(path.endswith(ext) for ext in static_ext):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return response

@app.post('/db')
def set_db():
    data = request.get_json(force=True) or {}
    cur = read_db()
    merged = {**cur}
    for k in DEFAULT.keys():
        if k in data:
            merged[k] = data[k]
    write_db(merged)
    return jsonify({"ok": True})

# Crear carpetas de medios si no existen
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)

@app.post('/upload/image')
def upload_image():
    f = request.files.get('file')
    if not f:
        return jsonify({"error": "file required"}), 400
    ext = os.path.splitext(f.filename)[1] or '.bin'
    fname = uuid.uuid4().hex + ext
    path = os.path.join(IMAGES_DIR, fname)
    f.save(path)
    return jsonify({"url": f"/media/images/{fname}"})

@app.post('/upload/video')
def upload_video():
    f = request.files.get('file')
    if not f:
        return jsonify({"error": "file required"}), 400
    ext = os.path.splitext(f.filename)[1] or '.mp4'
    fname = uuid.uuid4().hex + ext
    path = os.path.join(VIDEOS_DIR, fname)
    f.save(path)
    return jsonify({"url": f"/media/videos/{fname}"})

@app.post('/upload/chunk')
def upload_chunk():
    chunk = request.files.get('chunk')
    if not chunk:
        return jsonify({"error": "chunk required"}), 400
        
    upload_id = request.form.get('uploadId')
    chunk_index = int(request.form.get('chunkIndex', 0))
    total_chunks = int(request.form.get('totalChunks', 1))
    file_name = request.form.get('fileName')
    
    if not upload_id:
        return jsonify({"error": "uploadId required"}), 400

    # Temp file path
    temp_dir = os.path.join(MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{upload_id}.part")
    
    # Append chunk
    mode = 'ab' if chunk_index > 0 else 'wb'
    with open(temp_path, mode) as f:
        f.write(chunk.read())
        
    # Check if finished
    if chunk_index == total_chunks - 1:
        # Move to final destination
        ext = os.path.splitext(file_name)[1] if file_name else '.mp4'
        final_name = f"{uuid.uuid4().hex}{ext}"
        final_path = os.path.join(VIDEOS_DIR, final_name)
        
        os.rename(temp_path, final_path)
        
        # Auto-Notification
        try:
            cur = read_db()
            notif = {
                "id": str(uuid.uuid4()),
                "title": "Nuevo Contenido",
                "message": f"Se ha añadido nuevo contenido: {file_name}",
                "date": int(__import__('time').time() * 1000),
                "read": False
            }
            if "notifications" not in cur:
                cur["notifications"] = []
            cur["notifications"].insert(0, notif)
            write_db(cur)
        except Exception as e:
            print(f"Error creating notification: {e}")
            
        return jsonify({"url": f"/media/videos/{final_name}", "done": True})
        
    return jsonify({"done": False})

@app.get('/media/<path:subpath>')
def serve_media(subpath):
    response = send_from_directory(MEDIA_ROOT, subpath, as_attachment=False)
    response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return response

@app.post('/delete')
def delete_media():
    data = request.get_json(force=True) or {}
    url = data.get('url') or data.get('path') or ''
    if not url:
        return jsonify({"error": "path required"}), 400
    # Permitir formas: '/media/images/xxx', 'http://host:8001/media/videos/xxx'
    try:
        if url.startswith('http://') or url.startswith('https://'):
            from urllib.parse import urlparse
            p = urlparse(url).path
        else:
            p = url
        if not p.startswith('/media/'):
            return jsonify({"error": "invalid path"}), 400
        fs_path = os.path.normpath(os.path.join(MEDIA_ROOT, p.replace('/media/', '')))
        if not fs_path.startswith(MEDIA_ROOT):
            return jsonify({"error": "invalid path"}), 400
        if os.path.exists(fs_path):
            os.remove(fs_path)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get('/delete')
def delete_media_get():
    url = request.args.get('url') or request.args.get('path') or ''
    if not url:
        return jsonify({"error": "path required"}), 400
    try:
        if url.startswith('http://') or url.startswith('https://'):
            from urllib.parse import urlparse
            p = urlparse(url).path
        else:
            p = url
        if not p.startswith('/media/'):
            return jsonify({"error": "invalid path"}), 400
        fs_path = os.path.normpath(os.path.join(MEDIA_ROOT, p.replace('/media/', '')))
        if not fs_path.startswith(MEDIA_ROOT):
            return jsonify({"error": "invalid path"}), 400
        if os.path.exists(fs_path):
            os.remove(fs_path)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post('/api/notifications/send')
def send_notification():
    data = request.get_json(force=True) or {}
    title = data.get('title')
    message = data.get('message')
    
    if not title or not message:
        return jsonify({"error": "title and message required"}), 400
        
    cur = read_db()
    notif = {
        "id": str(uuid.uuid4()),
        "title": title,
        "message": message,
        "date": int(__import__('time').time() * 1000),
        "read": False
    }
    
    if "notifications" not in cur:
        cur["notifications"] = []
    
    # Add to start of list
    cur["notifications"].insert(0, notif)
    
    # Limit to last 50 notifications
    cur["notifications"] = cur["notifications"][:50]
    
    write_db(cur)
    return jsonify({"ok": True, "notification": notif})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
