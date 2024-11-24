import boto3
import os
import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1

# Initialize AWS clients
s3 = boto3.client('s3')

# Set Torch environment to Lambda's temporary storage
os.environ["TORCH_HOME"] = "/tmp"

# Initialize MTCNN and InceptionResnetV1
mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def lambda_handler(event, context):
    image_bucket = '1224979548-stage-1'  # Bucket containing images
    image_file_name = event['image_file_name']

    # Define buckets and file paths
    data_bucket = '1224979548-data'  # Bucket containing data.pt
    data_file_name = 'data.pt'
    tmp_image_path = f"/tmp/{image_file_name}"
    tmp_data_path = "/tmp/data.pt"

    try:
        # Download the image from the image bucket
        print(f"Downloading image from bucket: {image_bucket}, file: {image_file_name}")
        s3.download_file(image_bucket, image_file_name, tmp_image_path)
        print(f"Image successfully downloaded to {tmp_image_path}")

        # Download `data.pt` from the data bucket
        print(f"Downloading data file from bucket: {data_bucket}, file: {data_file_name}")
        s3.download_file(data_bucket, data_file_name, tmp_data_path)
        print(f"Data file successfully downloaded to {tmp_data_path}")
    except s3.exceptions.NoSuchKey as e:
        print(f"File not found: {e}")
        return {'statusCode': 404, 'body': f"Error: File not found - {str(e)}"}
    except s3.exceptions.NoSuchBucket as e:
        print(f"Bucket not found: {e}")
        return {'statusCode': 404, 'body': f"Error: Bucket not found - {str(e)}"}
    except Exception as e:
        print(f"Unexpected error during file download: {e}")
        return {'statusCode': 500, 'body': f"Unexpected error - {str(e)}"}

    # Perform face recognition
    try:
        name, distance = face_match(tmp_image_path, tmp_data_path)
        if name:
            output_bucket = "1224979548-output"
            output_key = image_file_name.replace('.jpg', '.txt')
            result_txt_path = f"/tmp/{output_key}"

            with open(result_txt_path, 'w') as result_file:
                result_file.write(name)

            # Upload the results to the output bucket
            s3.upload_file(result_txt_path, output_bucket, output_key)
            print(f"Result successfully saved to {output_bucket}/{output_key}")
            return {'statusCode': 200, 'body': f"Face recognized and result saved to {output_bucket}/{output_key}"}
        else:
            print(f"No face detected in image: {image_file_name}")
            return {'statusCode': 404, 'body': f"No face detected in {image_file_name}"}
    except Exception as e:
        print(f"Error during face recognition: {e}")
        return {'statusCode': 500, 'body': f"Error during face recognition - {str(e)}"}

def face_match(img_path, data_path):
    # Load the image and detect the face using MTCNN
    img = Image.open(img_path)
    face, prob = mtcnn(img, return_prob=True)
    if face is not None:
        # Generate the embedding for the detected face
        emb = resnet(face.unsqueeze(0)).detach()

        # Load the saved embeddings and names from `data.pt`
        saved_data = torch.load(data_path)
        embedding_list = saved_data[0]
        name_list = saved_data[1]

        # Compare the input face embedding with the saved embeddings
        dist_list = [torch.dist(emb, emb_db).item() for emb_db in embedding_list]
        idx_min = dist_list.index(min(dist_list))  # Closest match

        return name_list[idx_min], min(dist_list)

    return None, None
