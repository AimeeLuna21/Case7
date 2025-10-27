from flask import Flask, request, jsonify, render_template
import datetime, os, werkzeug
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient  # ✅ Required import

# Load local environment variables
load_dotenv()

# ---------- Configuration ----------

CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "lanternfly-images-ki3tmbyz"

# Create Blob Service Client
bsc = BlobServiceClient.from_connection_string(CONNECTION_STRING)
cc = bsc.get_container_client(CONTAINER_NAME)
# cc.url gives you the base URL to that container (for example: https://aimeecase7warmup.blob.core.windows.net/lanternfly-images)

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")


# ---------- API 1: Upload ----------
@app.post("/api/v1/upload")
def upload():
    try:
        # Get uploaded file from form-data
        f = request.files["file"]

        # Sanitize filename
        original_name = werkzeug.utils.secure_filename(f.filename)

        # Create timestamped name
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        blob_name = f"{timestamp}-{original_name}"

        # Upload to Azure Blob
        blob_client = cc.get_blob_client(blob_name)
        blob_client.upload_blob(f, overwrite=True)

        # Return JSON response with full blob URL
        return jsonify(ok=True, url=f"{cc.url}/{blob_name}")

    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


# ---------- API 2: Gallery ----------
@app.get("/api/v1/gallery")
def gallery():
    try:
        # List all blobs and build public URLs
        blobs = [f"{cc.url}/{b.name}" for b in cc.list_blobs()]
        return jsonify(ok=True, gallery=blobs)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


# ---------- API 3: Health Check ----------
@app.get("/api/v1/health")
def health():
    return jsonify(ok=True, status="healthy")
