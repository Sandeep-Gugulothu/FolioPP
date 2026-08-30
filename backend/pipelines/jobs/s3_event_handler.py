from ray.job_submission import JobSubmissionClient

def handle_s3_event(event, context):
    """Triggered by S3 Upload -> Submits Ray Job."""
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    client = JobSubmissionClient("http://rag-ray-cluster-head-svc:8265")
    client.submit_job(
        entrypoint=f"python pipelines/ingestion/main.py {bucket} {key}",
        runtime_env={"working_dir": "./"}
    )
