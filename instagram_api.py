import requests, time
from moviepy.editor import VideoFileClip
import pytz, time, configparser

config = configparser.ConfigParser()

# Config variables
config.read('settings.ini')
access_token = config['INSTAGRAM CREDS']['access_token']

def remove_newlines_and_empty(lst):
    # Remove "\n" from each element and filter out empty elements
    cleaned_lst = [element.rstrip('\n') for element in lst if element.strip()]
    return cleaned_lst

with open('instagram_user_ids.txt', 'r') as f:
    instagram_user_ids = f.readlines()

instagram_user_ids = remove_newlines_and_empty(instagram_user_ids) # Cleaning list

def preprocess_video(input_path, target_duration=60):
    video = VideoFileClip(input_path)

    # Define the new resolution (e.g., 576x1024)
    new_resolution = (576, 1024)

    # Resize the video to fit within the new resolution
    video_resized = video.resize(new_resolution)

    # Set the duration of the video
    video_duration_changed = video_resized.subclip(0, target_duration)

    # Save the modified video
    video_duration_changed.write_videofile("output.mp4", codec="libx264")

def upload_photo(photo_url, caption):
    for user_id in instagram_user_ids:
        # Create the media container
        create_media_url = f'https://graph.facebook.com/v12.0/{user_id}/media'
        data = {
            'access_token': access_token,
            'image_url': photo_url,
            'caption': caption,
            'media_type': 'IMAGE'
        }
        response = requests.post(create_media_url, data=data)
        
        if response.status_code == 200:
            container_id = response.json().get('id')
            #print("Media container created successfully!")
            
            # Publish the media container
            publish_media_url = f'https://graph.facebook.com/v12.0/{user_id}/media_publish'
            publish_data = {
                'access_token': access_token,
                'creation_id': container_id
            }
            publish_response = requests.post(publish_media_url, data=publish_data)
            
            if publish_response.status_code == 200:
                print("Instagram photo published successfully!")
            else:
                print(f"Error publishing photo: {publish_response.text}")
        else:
            print(f"Error creating media container: {response.text}")

def upload_video(video_url, caption, retries=7, delay=10):
    for user_id in instagram_user_ids:
        # Step 1: Create the media container
        create_media_url = f'https://graph.facebook.com/v12.0/{user_id}/media'
        
        data = {
            'access_token': access_token,
            'media_type': 'REELS',
            'caption': caption,
            'video_url': video_url  # Use the direct video URL here
        }

        response = requests.post(create_media_url, data=data)
        
        if response.status_code == 200:
            container_id = response.json().get('id')
            #print("Media container created successfully!")

            # Step 2: Attempt to publish the media container
            publish_media_url = f'https://graph.facebook.com/v12.0/{user_id}/media_publish'
            publish_data = {
                'access_token': access_token,
                'creation_id': container_id
            }
            
            attempt = 0
            while attempt < retries:
                publish_response = requests.post(publish_media_url, data=publish_data)
                
                if publish_response.status_code == 200:
                    print("Instagram video published successfully!")
                    break
                else:
                    print(f"Error publishing video: {publish_response.text}")
                    attempt += 1
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    
            if attempt == retries:
                print("Failed to publish video after several attempts.")
        else:
            print(f"Error creating media container: {response.text}")
