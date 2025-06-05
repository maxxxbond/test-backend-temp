# TODO: Implement certificate generation logic

from typing import Dict, Any
from fastapi import Response

def generate_certificate_content(user_name: str, certificate_data: Dict[str, Any]) -> str:
    """
    Generate certificate content in plain text format.
    In a real application, this would use a PDF library or template.
    """
    return f"""
CERTIFICATE OF COMPLETION

This is to certify that

{user_name}

has successfully completed the

OSINT (Open Source Intelligence) Course

Date: {certificate_data['issued_at'][:10]}
Certificate ID: {certificate_data['id']}
    """

def prepare_certificate_response(user_id: str, certificate_content: str) -> Response:
    """
    Prepare HTTP response for certificate download.
    """
    return Response(
        content=certificate_content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=osint_certificate_{user_id}.txt"}
    )
