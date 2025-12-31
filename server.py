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
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(BASE_DIR, path)

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

@app.get('/media/<path:subpath>')
def serve_media(subpath):
    # Sirve archivos desde ./media
    return send_from_directory(MEDIA_ROOT, subpath, as_attachment=False)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
