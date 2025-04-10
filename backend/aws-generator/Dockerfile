# Use AWS Lambda Python 3.10 runtime as the base image
FROM public.ecr.aws/lambda/python:3.10

# Set the working directory
WORKDIR /var/task

# Copy application and dependency files into the container
COPY lambda_function.py generators.py requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -t .

# Download nltk data (if needed)
RUN python3 -m nltk.downloader -d /var/task/nltk_data names

# Copy the NLTK dataset into the image
#COPY nltk_data /var/task/nltk_data

# Define the Lambda function entry point
CMD ["lambda_function.lambda_handler"]
