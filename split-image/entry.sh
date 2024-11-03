#!/bin/sh
# Use the AWS Lambda Runtime Interface Emulator for local testing
if [ -x /usr/bin/aws-lambda-rie ]; then
    /usr/bin/aws-lambda-rie /usr/local/bin/python -m awslambdaric $@
else
    exec "$@"
fi