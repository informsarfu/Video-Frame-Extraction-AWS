from boto3 import client as boto3_client
import os
import argparse
import time

input_bucket = "1224979548-input"
output_bucket = "1224979548-stage-1"
test_cases = "dataset/"

start_time = time.time()
parser = argparse.ArgumentParser(description='Upload videos to input S3')
parser.add_argument('--num_request', type=int, help='Number of requests to process')
parser.add_argument('--access_key', type=str, help='ACCESS KEY of the grading IAM user')
parser.add_argument('--secret_key', type=str, help='SECRET KEY of the grading IAM user')
parser.add_argument('--input_bucket', type=str, help='Name of the input bucket, e.g. 1234567890-input')
parser.add_argument('--output_bucket', type=str, help='Name of the output bucket, e.g. 1234567890-stage-1')
parser.add_argument('--testcase_folder', type=str, help='the path of the folder where videos are saved, e.g. test_cases/test_case_1/')

args = parser.parse_args()

access_key = args.access_key
secret_key = args.secret_key
input_bucket = args.input_bucket
output_bucket = args.output_bucket
test_cases = args.testcase_folder
region = 'us-east-1'

s3 = boto3_client('s3', aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key, region_name=region)

def clear_input_bucket(input_bucket):
    global s3
    list_obj = s3.list_objects_v2(Bucket=input_bucket)
    try:
        for item in list_obj["Contents"]:
            key = item["Key"]
            s3.delete_object(Bucket=input_bucket, Key=key)
    except:
        print("Nothing to clear in input bucket")
    
def clear_output_bucket(output_bucket):
    global s3
    list_obj = s3.list_objects_v2(Bucket=output_bucket)
    try:
        for item in list_obj["Contents"]:
            key = item["Key"]
            s3.delete_object(Bucket=output_bucket, Key=key)
    except:
        print("Nothing to clear in output bucket")

def upload_to_input_bucket_s3(input_bucket, path, name):
    global s3
    s3.upload_file(path + name, input_bucket, name)

def upload_files(input_bucket, test_dir, num_requests):
    uploaded_count = 0
    for filename in os.listdir(test_dir):
        if filename.endswith(".mp4") or filename.endswith(".MP4"):
            if uploaded_count < num_requests:
                print("Uploading to input bucket.. name: " + str(filename)) 
                upload_to_input_bucket_s3(input_bucket, test_dir, filename)
                uploaded_count += 1
            else:
                print("Reached the limit of uploads specified.")
                break

clear_input_bucket(input_bucket)
clear_output_bucket(output_bucket)

# Call the upload_files function with the number of requests
upload_files(input_bucket, test_cases, args.num_request)

end_time = time.time()
print("Time to run = ", end_time - start_time, "(seconds)")
print(f"Timestamps: start {start_time}, end {end_time}")
