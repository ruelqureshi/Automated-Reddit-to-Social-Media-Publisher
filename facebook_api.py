import requests
from moviepy.editor import VideoFileClip
import pytz, time, configparser

config = configparser.ConfigParser()

# Config variables
config.read('settings.ini')
access_token = config['FACEBOOK CREDS']['access_token']

def remove_newlines_and_empty(lst):
    # Remove "\n" from each element and filter out empty elements
    cleaned_lst = [element.rstrip('\n') for element in lst if element.strip()]
    return cleaned_lst

with open('facebook_pages.txt', 'r') as f:
    facebook_pages = f.readlines()

page_ids = remove_newlines_and_empty(facebook_pages) # Cleaning list

# Function to edit video using moviepy
def edit_video(input_path, duration=60):
    video = VideoFileClip(input_path)

    # Define the new resolution (e.g., 576x1024)
    new_resolution = (576, 1024)

    # Resize the video to fit within the new resolution
    video_resized = video.resize(new_resolution)

    # Set the duration of the video
    video_duration_changed = video_resized.subclip(0, duration)

    # Save the modified video
    video_duration_changed.write_videofile("output.mp4", codec="libx264")

# Function to upload video as a Reel
def upload_video_fb(file_path, description):
    file_path = 'output.mp4'
    for page_id in page_ids:
        video_endpoint = f'https://graph.facebook.com/v12.0/{page_id}/videos'
        with open(file_path, 'rb') as video_file:
            files = {
                'file': video_file
            }
            data = {
                'description': description,
                'access_token': access_token
            }
            response = requests.post(video_endpoint, files=files, data=data)
            if response.status_code == 200:
                print("Video uploaded successfully!")
            else:
                print(f"Error uploading video: {response.text}")

# Function to upload photo
def upload_photo_fb(image_url, caption):
    for page_id in page_ids:
        photo_endpoint = f'https://graph.facebook.com/v12.0/{page_id}/photos'
        data = {
            'caption': caption,
            'url': image_url,
            'access_token': access_token
        }
        response = requests.post(photo_endpoint, data=data)
        if response.status_code == 200:
            print("Photo uploaded successfully!")
        else:
            print(f"Error uploading photo: {response.text}")