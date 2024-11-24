# FROM python:3.8-slim

# # Set working directory inside the container
# WORKDIR /var/task

# # Install system dependencies (e.g., OpenCV)
# RUN apt-get update && apt-get install -y \
#     libglib2.0-0 \
#     libsm6 \
#     libxext6 \
#     libxrender-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Install required Python packages
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Install AWS Lambda Runtime Interface Client
# RUN pip install awslambdaric

# # Copy the face-recognition code into the container
# COPY face_recognition_code.py .

# # Set the entrypoint to the Lambda Runtime Interface Client
# ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

# # Set the CMD to your Lambda handler
# CMD [ "face_recognition_code.lambda_handler" ]


FROM public.ecr.aws/lambda/python:3.8

# Install system dependencies
RUN yum update -y && yum install -y \
    mesa-libGL \
    && yum clean all

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install Python packages
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy function code
COPY face_recognition_code.py ${LAMBDA_TASK_ROOT}
COPY tmp/data.pt ${LAMBDA_TASK_ROOT}/data.pt

# Set the CMD to your handler
CMD [ "face_recognition_code.lambda_handler" ]