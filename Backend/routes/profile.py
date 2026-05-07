import os
import uuid
import boto3
from flask import Blueprint, request, jsonify, session
from db import get_db

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")

S3_BUCKET = os.environ.get("S3_BUCKET", "user-profile-images-910520206984-us-east-2-an")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")


def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)


@profile_bp.route("/image", methods=["POST"])
def upload_profile_image():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Login required"}), 401

    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Validate file type
    allowed = {"png", "jpg", "jpeg", "gif", "webp"}
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed:
        return jsonify({"error": f"File type .{ext} not allowed"}), 400

    # Upload to S3
    filename = f"profiles/{user_id}/{uuid.uuid4().hex}.{ext}"
    try:
        s3 = get_s3_client()
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            filename,
            ExtraArgs={"ContentType": file.content_type},
        )
        image_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

    # Update database
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE users SET profile_image = %s WHERE user_id = %s", (image_url, user_id))
    db.commit()

    return jsonify({"message": "Profile image updated", "image_url": image_url})