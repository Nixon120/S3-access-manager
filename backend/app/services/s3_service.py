import boto3
from botocore.exceptions import ClientError
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.config import settings
from app.models.s3_connection import S3Connection, AuthMethod
import logging

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        """Initialize default S3 client from env vars"""
        self._default_client = self._create_client_from_env()

    def _create_client_from_env(self):
        """Create S3 client using environment variables"""
        session_kwargs = {
            'region_name': settings.AWS_REGION
        }
        
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY_ID
            session_kwargs['aws_secret_access_key'] = settings.AWS_SECRET_ACCESS_KEY
            
        return boto3.client('s3', **session_kwargs)

    def get_client(self, connection: Optional[S3Connection] = None):
        """
        Get S3 client, either default or from specific connection
        """
        if not connection:
            return self._default_client
            
        try:
            session_kwargs = {
                'region_name': connection.region
            }
            
            if connection.auth_method == AuthMethod.ACCESS_KEY:
                session_kwargs['aws_access_key_id'] = connection.access_key_id
                session_kwargs['aws_secret_access_key'] = connection.secret_access_key
                
            elif connection.auth_method == AuthMethod.IAM_ROLE:
                # Assume role logic
                sts_client = boto3.client('sts', region_name=connection.region)
                assume_role_kwargs = {
                    'RoleArn': connection.role_arn,
                    'RoleSessionName': 'S3AccessManagerSession'
                }
                if connection.external_id:
                    assume_role_kwargs['ExternalId'] = connection.external_id
                    
                assumed_role = sts_client.assume_role(**assume_role_kwargs)
                credentials = assumed_role['Credentials']
                
                session_kwargs['aws_access_key_id'] = credentials['AccessKeyId']
                session_kwargs['aws_secret_access_key'] = credentials['SecretAccessKey']
                session_kwargs['aws_session_token'] = credentials['SessionToken']
                
            # TODO: Implement IAM_ROLES_ANYWHERE support if needed
            
            return boto3.client('s3', **session_kwargs)
            
        except Exception as e:
            logger.error(f"Error creating S3 client for connection {connection.name}: {e}")
            raise

    def generate_presigned_url(
        self,
        bucket_name: str,
        object_key: str,
        operation: str = "get_object",
        expiration: int = None,
        connection: Optional[S3Connection] = None
    ) -> str:
        """Generate a presigned URL for S3 operations"""
        if expiration is None:
            expiration = settings.PRESIGNED_URL_EXPIRATION
        
        try:
            client = self.get_client(connection)
            url = client.generate_presigned_url(
                ClientMethod=operation,
                Params={
                    'Bucket': bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def generate_presigned_post(
        self,
        bucket_name: str,
        object_key: str,
        expiration: int = None,
        max_size: int = None,
        connection: Optional[S3Connection] = None
    ) -> Dict:
        """Generate a presigned POST for direct browser uploads"""
        if expiration is None:
            expiration = settings.PRESIGNED_URL_EXPIRATION
        
        if max_size is None:
            max_size = settings.MAX_UPLOAD_SIZE
        
        conditions = [
            {"bucket": bucket_name},
            ["starts-with", "$key", object_key],
            ["content-length-range", 0, max_size]
        ]
        
        try:
            client = self.get_client(connection)
            response = client.generate_presigned_post(
                Bucket=bucket_name,
                Key=object_key,
                Conditions=conditions,
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"Error generating presigned POST: {e}")
            raise
    
    def list_objects(
        self,
        bucket_name: str,
        prefix: str = "",
        max_keys: int = 1000,
        connection: Optional[S3Connection] = None
    ) -> List[Dict]:
        """List objects in an S3 bucket with prefix"""
        try:
            client = self.get_client(connection)
            response = client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    objects.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj['ETag'].strip('"')
                    })
            
            return objects
        except ClientError as e:
            logger.error(f"Error listing objects: {e}")
            raise
    
    def get_object_metadata(
        self,
        bucket_name: str,
        object_key: str,
        connection: Optional[S3Connection] = None
    ) -> Dict:
        """Get metadata for a specific S3 object"""
        try:
            client = self.get_client(connection)
            response = client.head_object(
                Bucket=bucket_name,
                Key=object_key
            )
            
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response.get('ContentType'),
                'etag': response['ETag'].strip('"'),
                'metadata': response.get('Metadata', {})
            }
        except ClientError as e:
            logger.error(f"Error getting object metadata: {e}")
            raise
    
    def check_bucket_access(self, bucket_name: str, connection: Optional[S3Connection] = None) -> bool:
        """Check if the application has access to a bucket"""
        try:
            client = self.get_client(connection)
            client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError:
            return False
    
    def list_buckets(self, connection: Optional[S3Connection] = None) -> List[str]:
        """List all accessible S3 buckets"""
        try:
            client = self.get_client(connection)
            response = client.list_buckets()
            return [bucket['Name'] for bucket in response['Buckets']]
        except ClientError as e:
            logger.error(f"Error listing buckets: {e}")
            raise
    
    def test_connection(self, connection: S3Connection) -> Dict[str, Any]:
        """
        Test if a connection is valid by listing buckets
        Returns dict with success status and bucket count or error message
        """
        try:
            client = self.get_client(connection)
            response = client.list_buckets()
            return {
                "success": True,
                "bucket_count": len(response['Buckets']),
                "message": f"Successfully connected. Found {len(response['Buckets'])} buckets."
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }


# Singleton instance
s3_service = S3Service()
