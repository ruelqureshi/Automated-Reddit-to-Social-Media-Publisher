import os
import time
import json
from requests_oauthlib import OAuth1Session

# Open and read the JSON file
with open('x_creds.json', 'r') as file:
    parsed_data = json.load(file)

def post_tweet(tweet_text, media_id, oauth):
    tweet_url = "https://api.twitter.com/2/tweets"
    payload = {
        "text": tweet_text,
        "media": {
            "media_ids": [media_id]
        }
    }

    response = oauth.post(tweet_url, json=payload)

    if response.status_code != 201:
        print(f"Tweet posting failed: {response.status_code} {response.text}")
        raise Exception(f"Tweet posting failed: {response.status_code} {response.text}")

    print(f"Tweet posted successfully: {response.json()}")

def check_media_status(media_id, oauth):
    STATUS_URL = "https://upload.twitter.com/1.1/media/upload.json"
    status_data = {
        "command": "STATUS",
        "media_id": media_id
    }
    while True:
        response = oauth.get(STATUS_URL, params=status_data)
        if response.status_code != 200:
            print(f"STATUS command failed: {response.status_code} {response.text}")
            raise Exception(f"STATUS command failed: {response.status_code} {response.text}")

        processing_info = response.json().get("processing_info", {})
        state = processing_info.get("state")

        if state == "succeeded":
            return
        elif state == "failed":
            error_message = processing_info.get("error", {}).get("message", "Unknown error")
            print(f"Media processing failed: {error_message}")
            raise Exception(f"Media processing failed: {error_message}")

        check_after_secs = processing_info.get("check_after_secs", 5)
        time.sleep(check_after_secs)

def upload_photo_x(file_path, tweet_text):
    for creds in parsed_data:
        oauth = OAuth1Session(
            client_key=creds["client_key"],
            client_secret=creds["client_secret"],
            resource_owner_key=creds["access_token"],
            resource_owner_secret=creds["access_token_secret"]
        )

        media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"

        with open(file_path, 'rb') as file:
            media_data = file.read()

        response = oauth.post(media_upload_url, files={"media": media_data})

        if response.status_code != 200:
            print(f"Media upload failed: {response.status_code} {response.text}")
            raise Exception(f"Media upload failed: {response.status_code} {response.text}")

        media_id = response.json().get("media_id_string")
        #print(f"Media uploaded successfully, media_id: {media_id}")

        if not media_id:
            raise Exception("Invalid media ID returned from upload")

        post_tweet(tweet_text, media_id, oauth)

def upload_video_x(file_path, tweet_text):
    for creds in parsed_data:
        oauth = OAuth1Session(
            client_key=creds["client_key"],
            client_secret=creds["client_secret"],
            resource_owner_key=creds["access_token"],
            resource_owner_secret=creds["access_token_secret"]
        )
        INIT_URL = "https://upload.twitter.com/1.1/media/upload.json"
        APPEND_URL = "https://upload.twitter.com/1.1/media/upload.json"
        FINALIZE_URL = "https://upload.twitter.com/1.1/media/upload.json"

        total_bytes = os.path.getsize(file_path)
        media_type = "video/mp4"
        init_data = {
            "command": "INIT",
            "total_bytes": total_bytes,
            "media_type": media_type,
        }
        response = oauth.post(INIT_URL, data=init_data)

        if response.status_code != 202:
            print(f"INIT command failed: {response.status_code} {response.text}")
            raise Exception(f"INIT command failed: {response.status_code} {response.text}")

        media_id = response.json()["media_id_string"]
        #print(f"INIT successful, media_id: {media_id}")

        segment_id = 0
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(4 * 1024 * 1024)
                if not chunk:
                    break
                append_data = {
                    "command": "APPEND",
                    "media_id": media_id,
                    "segment_index": segment_id,
                }
                files = {"media": chunk}
                response = oauth.post(APPEND_URL, data=append_data, files=files)
                if response.status_code != 204:
                    print(f"APPEND command failed: {response.status_code} {response.text}")
                    raise Exception(f"APPEND command failed: {response.status_code} {response.text}")
                segment_id += 1

        finalize_data = {
            "command": "FINALIZE",
            "media_id": media_id,
        }
        response = oauth.post(FINALIZE_URL, data=finalize_data)
        if response.status_code != 200:
            print(f"FINALIZE command failed: {response.status_code} {response.text}")
            raise Exception(f"FINALIZE command failed: {response.status_code} {response.text}")

        #print("FINALIZE successful, checking media status")
        check_media_status(media_id, oauth)

        post_tweet(tweet_text, media_id, oauth)

def upload_gif_x(file_path, tweet_text):
    for creds in parsed_data:
        oauth = OAuth1Session(
            client_key=creds["client_key"],
            client_secret=creds["client_secret"],
            resource_owner_key=creds["access_token"],
            resource_owner_secret=creds["access_token_secret"]
        )
        INIT_URL = "https://upload.twitter.com/1.1/media/upload.json"
        APPEND_URL = "https://upload.twitter.com/1.1/media/upload.json"
        FINALIZE_URL = "https://upload.twitter.com/1.1/media/upload.json"

        total_bytes = os.path.getsize(file_path)
        media_type = "video/mp4"
        init_data = {
            "command": "INIT",
            "total_bytes": total_bytes,
            "media_type": media_type,
        }
        response = oauth.post(INIT_URL, data=init_data)

        if response.status_code != 202:
            print(f"INIT command failed: {response.status_code} {response.text}")
            raise Exception(f"INIT command failed: {response.status_code} {response.text}")

        media_id = response.json()["media_id_string"]
        print(f"INIT successful, media_id: {media_id}")

        segment_id = 0
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(4 * 1024 * 1024)  # 4MB chunks
                if not chunk:
                    break
                append_data = {
                    "command": "APPEND",
                    "media_id": media_id,
                    "segment_index": segment_id,
                }
                files = {"media": chunk}
                response = oauth.post(APPEND_URL, data=append_data, files=files)
                if response.status_code != 204:
                    print(f"APPEND command failed: {response.status_code} {response.text}")
                    raise Exception(f"APPEND command failed: {response.status_code} {response.text}")
                segment_id += 1

        finalize_data = {
            "command": "FINALIZE",
            "media_id": media_id,
        }
        response = oauth.post(FINALIZE_URL, data=finalize_data)
        if response.status_code != 200:
            print(f"FINALIZE command failed: {response.status_code} {response.text}")
            raise Exception(f"FINALIZE command failed: {response.status_code} {response.text}")

        print("FINALIZE successful, checking media status")
        check_media_status(media_id, oauth)

        post_tweet(tweet_text, media_id, oauth)