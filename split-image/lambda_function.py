import boto3
import os
import subprocess
from urllib.parse import unquote_plus
import json

lambda_client = boto3.client('lambda')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Extract bucket and object key from the event
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    video_filename = object_key.split('/')[-1]
    video_name = video_filename.rsplit('.', 1)[0]
    stage1_bucket = f"{input_bucket.split('-')[0]}-stage-1"  # Use input bucket to form stage-1 bucket name

    # Define local paths for downloading and processing
    input_video_path = f"/tmp/{video_filename}"
    output_dir = f"/tmp/{video_name}"
    os.makedirs(output_dir, exist_ok=True)

    # Download the video from the input bucket
    s3.download_file(input_bucket, object_key, input_video_path)

    # Use ffmpeg to extract a single frame (first frame) from the video
    ffmpeg_command = [
        '/usr/local/bin/ffmpeg', '-i', input_video_path,
        '-vf', 'fps=1', '-vframes', '1', 
        f"{output_dir}/output.jpg", '-y'
    ]
    subprocess.run(ffmpeg_command, check=True)

    # Upload the frame to stage-1 bucket
    frame_filename = f"{video_name}.jpg"
    s3.upload_file(f"{output_dir}/output.jpg", stage1_bucket, frame_filename)

    # Trigger face-recognition function asynchronously
    lambda_payload = {
        "bucket_name": stage1_bucket,
        "image_file_name": frame_filename
    }
    
    lambda_client.invoke(
        FunctionName='face-recognition', 
        InvocationType='Event',
        Payload=json.dumps(lambda_payload)
    )

    return {
        'statusCode': 200,
        'body': f"Video {video_filename} processed and frame saved to {stage1_bucket}/{frame_filename}"
    }
