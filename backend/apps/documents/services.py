"""S3 presigned URL service for document vault."""

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from apps.documents.models import ChecklistStatus, LandDocumentChecklistItem


class S3ServiceError(Exception):
    """Raised when S3 operations fail."""

    pass


class S3NotConfiguredError(S3ServiceError):
    """Raised when AWS credentials are not configured."""

    pass


def _get_s3_client():
    """Get S3 client with credentials from settings, or None if not configured."""
    bucket = getattr(settings, "AWS_S3_BUCKET_NAME", None)
    access_key = getattr(settings, "AWS_ACCESS_KEY_ID", None)
    secret_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
    region = getattr(settings, "AWS_S3_REGION_NAME", "us-east-1")

    if not bucket:
        return None

    kwargs = {"region_name": region}
    if access_key and secret_key:
        kwargs["aws_access_key_id"] = access_key
        kwargs["aws_secret_access_key"] = secret_key

    return boto3.client("s3", **kwargs)


def _is_configured():
    """Check if AWS S3 is properly configured."""
    bucket = getattr(settings, "AWS_S3_BUCKET_NAME", None)
    return bool(bucket)


def _get_expiry_seconds():
    """Get presign expiry seconds from settings."""
    return getattr(settings, "AWS_S3_PRESIGN_EXPIRY_SECONDS", 3600)


def generate_presigned_upload_url(
    s3_key: str,
    content_type: str,
    filename: str = None,
) -> tuple[str, int]:
    """
    Generate a presigned URL for uploading a document to S3.

    Returns:
        tuple: (presigned_url, expiry_seconds)

    Raises:
        S3NotConfiguredError: If AWS is not configured
        S3ServiceError: If the operation fails
    """
    if not _is_configured():
        raise S3NotConfiguredError(
            "AWS S3 is not configured. Set AWS_S3_BUCKET_NAME and AWS credentials."
        )

    client = _get_s3_client()
    bucket = settings.AWS_S3_BUCKET_NAME
    expiry = _get_expiry_seconds()

    extra_args = {"ContentType": content_type}
    if filename:
        extra_args["ContentDisposition"] = f'inline; filename="{filename}"'

    try:
        url = client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket,
                "Key": s3_key,
                "ContentType": content_type,
            },
            ExpiresIn=expiry,
        )
    except ClientError as e:
        raise S3ServiceError(f"Failed to generate presigned upload URL: {e}")

    return url, expiry


def generate_presigned_download_url(s3_key: str) -> tuple[str, int]:
    """
    Generate a presigned URL for downloading a document from S3.

    Returns:
        tuple: (presigned_url, expiry_seconds)

    Raises:
        S3NotConfiguredError: If AWS is not configured
        S3ServiceError: If the operation fails
    """
    if not _is_configured():
        raise S3NotConfiguredError(
            "AWS S3 is not configured. Set AWS_S3_BUCKET_NAME and AWS credentials."
        )

    client = _get_s3_client()
    bucket = settings.AWS_S3_BUCKET_NAME
    expiry = _get_expiry_seconds()

    try:
        url = client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket,
                "Key": s3_key,
            },
            ExpiresIn=expiry,
        )
    except ClientError as e:
        raise S3ServiceError(f"Failed to generate presigned download URL: {e}")

    return url, expiry


def check_object_exists(s3_key: str) -> bool:
    """
    Check if an object exists in S3.

    Returns:
        bool: True if the object exists

    Raises:
        S3NotConfiguredError: If AWS is not configured
    """
    if not _is_configured():
        raise S3NotConfiguredError(
            "AWS S3 is not configured. Set AWS_S3_BUCKET_NAME and AWS credentials."
        )

    client = _get_s3_client()
    bucket = settings.AWS_S3_BUCKET_NAME

    try:
        client.head_object(Bucket=bucket, Key=s3_key)
        return True
    except ClientError:
        return False


def delete_object(s3_key: str) -> None:
    """
    Delete an object from S3.

    Raises:
        S3NotConfiguredError: If AWS is not configured
        S3ServiceError: If the operation fails
    """
    if not _is_configured():
        raise S3NotConfiguredError(
            "AWS S3 is not configured. Set AWS_S3_BUCKET_NAME and AWS credentials."
        )

    client = _get_s3_client()
    bucket = settings.AWS_S3_BUCKET_NAME

    try:
        client.delete_object(Bucket=bucket, Key=s3_key)
    except ClientError as e:
        raise S3ServiceError(f"Failed to delete object: {e}")


def calculate_land_completion(land_id: str) -> float:
    """
    Calculate document completion percentage for a land.

    Formula: (Count of items where checklist_status='CERTIFIED_OBTAINED') /
             (Total items where checklist_status != 'NOT_APPLICABLE')

    Returns:
        float: 0.0 to 1.0 representing completion percentage

    Raises:
        ValueError: If land_id is not found
    """
    from apps.land.models import LandFile

    try:
        land = LandFile.objects.get(land_id=land_id)
    except LandFile.DoesNotExist:
        raise ValueError(f"Land with land_id '{land_id}' not found")

    items = LandDocumentChecklistItem.objects.filter(land=land, is_deleted=False)

    total_applicable = items.exclude(
        checklist_status=ChecklistStatus.NOT_APPLICABLE
    ).count()

    if total_applicable == 0:
        return 0.0

    certified_count = items.filter(
        checklist_status=ChecklistStatus.CERTIFIED_OBTAINED
    ).count()

    return certified_count / total_applicable


def get_overall_completion_stats() -> float:
    """
    Get average document completion across all lands.

    Returns:
        float: 0.0 to 1.0 representing average completion percentage
    """
    from apps.land.models import LandFile

    lands = LandFile.objects.filter(is_deleted=False)

    if not lands.exists():
        return 0.0

    total_completion = 0.0
    count = 0

    for land in lands:
        completion = calculate_land_completion(land.land_id)
        total_completion += completion
        count += 1

    if count == 0:
        return 0.0

    return total_completion / count
