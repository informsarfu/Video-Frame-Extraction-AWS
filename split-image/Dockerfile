# Use AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Copy the precompiled ffmpeg binary into /usr/local/bin
COPY ffmpeg /usr/local/bin/ffmpeg

# Set executable permissions on the ffmpeg binary
RUN chmod +x /usr/local/bin/ffmpeg

# Copy the Lambda handler code to the container
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the Lambda handler function name
CMD ["lambda_function.lambda_handler"]





