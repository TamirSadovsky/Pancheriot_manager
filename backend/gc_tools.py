import logging
import tempfile
from datetime import datetime
import base64
from base64 import b64decode
import os
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)


def save_signature_gc(appointment_id: int, base64_str: str) -> str:
    """
    Saves the base64 signature image to GCS using AppointmentID and current datetime as filename.
    Returns the public URL.
    """
    # Format filename with timestamp
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"signatures/{appointment_id}_{now}.png"

    try:
        # Decode base64 image
        img_bytes = b64decode(base64_str.split(",")[-1])  # strip 'data:image/png;base64,'
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name

        # Upload to GCS
        url = upload_image_to_gcs(tmp_path, filename)
        print(f"✅ Signature uploaded to: {url}")
        return url

    except Exception as e:
        print(f"❌ Failed to save signature: {e}")
        return None

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def upload_image_to_gcs(local_file_path: str, destination_blob_name: str) -> str:
    """
    Uploads an image to Google Cloud Storage and returns a public URL.
    """
    try:
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)

        # ✅ Make the file publicly accessible
        blob.make_public()

        public_url = blob.public_url
        logging.info(f"✅ Image uploaded successfully: {public_url}")
        return public_url
    except Exception as e:
        logging.error(f"❌ Failed to upload image: {e}")
        return None


