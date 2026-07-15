import praw
import requests
from datetime import datetime
from instagram_api import upload_photo, upload_video, preprocess_video
from facebook_api import upload_photo_fb, upload_video_fb
from x_api import upload_photo_x, upload_video_x
from main_g_drive import upload_file, delete_file
from subprocess import run
import subprocess
import os, sys
from pytube import YouTube

if os.path.isfile('final_video.mp4'):
    os.remove('final_video.mp4')

# Function to download a file from a URL
def download_file(url, output_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
    else:
        print(f"Failed to download file from {url}")

# Function to merge video and audio using ffmpeg
def merge_video_audio(video_path, audio_path, output_path):
    run(['ffmpeg', '-i', video_path, '-i', audio_path, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', output_path], check=True)

def convert_gif_to_mp4(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-movflags", "faststart",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        output_path
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Conversion successful: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during conversion: {e}")

# Function to download YouTube video
def download_youtube_video(url, output_path):
    try:
        yt = YouTube(url)
        ys = yt.streams.get_highest_resolution()
        ys.download(filename=output_path)
        print(f"Downloaded YouTube video: {output_path}")
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")

# Define your Reddit app credentials
client_id = 'ie3Nvpz2jyYp-apiZ5lw9A'
client_secret = '-JPUtfZGI5rDBo2TNHBC3aKiU4rYcw'
user_agent = 'python:get_posts:v1.0 (by /u/raphaelkills)'

def reddit(subreddit_name):

    # Initialize the PRAW Reddit instance
    try:
        reddit = praw.Reddit(client_id=client_id,
                             client_secret=client_secret,
                             user_agent=user_agent)
    except Exception as e:
        print(f"Error initializing Reddit instance: {e}")
        exit()

    # Fetch the most upvoted post
    try:
        subreddit = reddit.subreddit(subreddit_name)
        top_post = next(subreddit.top(time_filter='all', limit=1))
    except Exception as e:
        print(f"Error fetching top post: {e}")
        exit()

    # Initialize an empty list to store the parsed data
    post_ids = []

    # Open the text file in read mode
    with open('log_file.txt', 'r') as file:
        # Read all lines from the file
        lines = file.readlines()
        
        # Iterate over each line in the file
        for line in lines:
            # Strip any extra whitespace and split the line into parts
            parts = line.strip().split(' - ')
            
            # Extract the Post ID, assuming it is the second part after splitting by ': '
            if len(parts) > 1:
                post_id = parts[1].split(': ')[1]
                post_ids.append(post_id)

    if top_post.id in post_ids:
        print(top_post.id)
        print(f"Top post is already posted.")
        print('Skipping.\n')
        return
    else:
        title = top_post.title
        title = title.strip('“”"\'')
        # Print the title, upvotes, link, and post ID of the most upvoted post
        print(f"Title: {title}")
        print(f"Upvotes: {top_post.score}")
        print(f"Link: https://www.reddit.com{top_post.permalink}")
        print(f"Post ID: {top_post.id}")

    # Check if the post contains an image
    if top_post.url.endswith(('jpg', 'jpeg', 'png', 'gif')):
        # Upload the image to Instagram
        caption = title  # You can use the post title as the caption

        if top_post.url.endswith(('jpg')):
            image_path = 'downloaded_image.jpg'
            download_file(top_post.url, image_path)
            upload_photo_x(image_path, caption)
        elif top_post.url.endswith(('jpeg')):
            image_path = 'downloaded_image.jpeg'
            download_file(top_post.url, image_path)
            upload_photo_x(image_path, caption)
        elif top_post.url.endswith(('png')):
            image_path = 'downloaded_image.png'
            download_file(top_post.url, image_path)
            upload_photo_x(image_path, caption)
        elif top_post.url.endswith(('gif')):
            image_path = 'downloaded_image.gif'
            download_file(top_post.url, image_path)
            convert_gif_to_mp4(image_path, 'gif.mp4')
            upload_video_x('gif.mp4', caption)
            os.remove('gif.mp4')
        
        upload_photo(top_post.url, caption)
        upload_photo_fb(top_post.url, caption)
        
        os.remove(image_path)
        
        # Log the post ID with timestamp to a file
        log_file_path = 'log_file.txt'
        with open(log_file_path, 'a') as file:
            file.write(f"{datetime.now()} - Post ID: {top_post.id}\n")
    else:
        print("No image found in the top post.")

    # Check if the post contains a YouTube link
    if 'youtube.com' in top_post.url or 'youtu.be' in top_post.url:
        youtube_video_path = 'downloaded_youtube_video.mp4'
        download_youtube_video(top_post.url, youtube_video_path)
        preprocess_video(youtube_video_path)

        # Example usage: Upload a file
        file = 'output.mp4'  # Path to the file you want to upload
        file_name = 'output.mp4'        # Name to give the uploaded file
        folder_id = '1bX5dId6P4QPtstqIwoAuHP5Zmj18ouYZ' # ID of the folder to upload the file into
            
        file_id = upload_file(file, file_name, folder_id)
        file_path = f'https://drive.google.com/uc?export=download&id={file_id}'
        
        caption = title  # You can use the post title as the caption
        upload_video(file_path, caption)
        upload_video_fb(file, caption)
        upload_video_x(youtube_video_path, caption)
        
        os.remove(youtube_video_path)
        os.remove(file)
        delete_file(file_id)

        # Log the post ID with timestamp to a file
        log_file_path = 'log_file.txt'
        with open(log_file_path, 'a') as file:
            file.write(f"{datetime.now()} - Post ID: {top_post.id}\n")
        return

    # Check if the post contains a video
    if hasattr(top_post, 'media') and top_post.media and 'reddit_video' in top_post.media:
        video_url = top_post.media['reddit_video']['fallback_url']
        
        # Derive the audio URL
        audio_url = video_url.replace("DASH_240.mp4", "DASH_audio.mp4")  # This might need to be adjusted based on the actual URL pattern

        video_path = 'downloaded_video.mp4'
        audio_path = 'downloaded_audio.mp4'
        final_video = 'final_video.mp4'

        # Download the video and audio
        download_file(video_url, video_path)
        download_file(audio_url, audio_path)
        
        # Verify if audio file is downloaded correctly and merge
        if os.path.getsize(audio_path) > 0:
            merge_video_audio(video_path, audio_path, final_video)
            preprocess_video(final_video)
            print(f"Video with audio saved to {final_video}")

            # Example usage: Upload a file
            file = 'output.mp4'  # Path to the file you want to upload
            file_name = 'output.mp4'        # Name to give the uploaded file
            folder_id = '1bX5dId6P4QPtstqIwoAuHP5Zmj18ouYZ' # ID of the folder to upload the file into
            
            file_id = upload_file(file, file_name, folder_id)
            file_path = f'https://drive.google.com/uc?export=download&id={file_id}'
            
            caption = top_post.title
            upload_video(file_path, caption)
            upload_video_fb(file, caption)
            upload_video_x(final_video, caption)
            
            # Clean up downloaded files
            os.remove(video_path)
            os.remove(audio_path)
            os.remove(final_video)
            os.remove(file)
            delete_file(file_id)

            # Log the post ID with timestamp to a file
            log_file_path = 'log_file.txt'
            with open(log_file_path, 'a') as file:
                file.write(f"{datetime.now()} - Post ID: {top_post.id}\n")
        else:
            print("Audio file is empty or not downloaded correctly.\n")
    else:
        print("No video found in the top post.\n")