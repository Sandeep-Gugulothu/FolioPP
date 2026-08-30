import os
import boto3
from concurrent.futures import ThreadPoolExecutor

def upload_file(args):
    file_path, bucket_name, s3_client = args
    key = os.path.basename(file_path)
    s3_client.upload_file(file_path, bucket_name, key)
    print(f"Uploaded {key}")

def upload_directory(dir_path, bucket_name):
    """High-performance multi-threaded S3 uploader."""
    s3_client = boto3.client('s3')
    files_to_upload = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Maps local files to S3 upload tasks
        executor.map(upload_file, [(f, bucket_name, s3_client) for f in files_to_upload])

if __name__ == "__main__":
    # upload_directory('data/', 'rag-platform-docs-dev')
    print("Runner for S3 bulk upload")
