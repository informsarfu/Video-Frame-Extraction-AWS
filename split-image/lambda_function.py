import boto3
import os
import subprocess
from urllib.parse import unquote_plus

# Initialize the S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Extract bucket and object key from the event
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    video_filename = object_key.split('/')[-1]
    video_name = video_filename.rsplit('.', 1)[0]
    stage1_bucket = "1224979548-stage-1"  # Output bucket

    # Define local paths for downloading and processing
    input_video_path = f"/tmp/{video_filename}"
    output_dir = f"/tmp/{video_name}"
    os.makedirs(output_dir, exist_ok=True)

    # Download the video from the input bucket
    s3.download_file(input_bucket, object_key, input_video_path)

    # Use ffmpeg to split the video into frames
    ffmpeg_command = [
        '/usr/local/bin/ffmpeg', '-i', input_video_path,
        '-vf', 'fps=5',  # Set to capture 5 frames per second
        f"{output_dir}/output-%02d.jpg", '-y'
    ]
    subprocess.run(ffmpeg_command, check=True)

    # Upload each frame to the stage-1 bucket
    for frame_filename in os.listdir(output_dir):
        frame_path = os.path.join(output_dir, frame_filename)
        s3.upload_file(frame_path, stage1_bucket, f"{video_name}/{frame_filename}")

    # Clean up temporary files
    os.remove(input_video_path)
    for frame_file in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, frame_file))

    return {
        'statusCode': 200,
        'body': f"Video {video_filename} processed and frames stored in {stage1_bucket}/{video_name}/"
    }
