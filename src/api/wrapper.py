import urllib.parse
from typing import Optional, Any

from src.api.client import post, get


def create_admin(name: str, email: str, affiliation: str):
    return post("/admins/create", json={
        "name": name,
        "email": email,
        "affiliation": affiliation,
    })


def import_csv_api(uploaded_file, institution, logo_path, template_type, template_path, admin_mail):
    if isinstance(uploaded_file, list):
        uploaded_file = uploaded_file[0]

    admin_mail_q = urllib.parse.quote(admin_mail)

    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")
    }
    data = {
        "institution": institution,
        "logo_path": logo_path or "",
        "template": template_type,
        "template_path": template_path,
    }
    return post(f"/certificates/import-csv?admin_mail={admin_mail_q}", files=files, data=data)

def set_alias_email(email: str, alias: str):
    return post("/users/alias", json={
        "main_email": email,
        "alias_email": alias
    })

def get_cert_template_path(cert_number: str) -> str:
    resp = get("/certificates/template-path", params={"cert_number": cert_number})
    return resp["template_path"]

def get_certificates_for_user_email(email: str):
    return get("/certificates/by-user", params={"email": email})

def get_certificates_for_admin_email(email: str):
    return get("/certificates/by-admin", params={"email": email})

def apply_certificate_editor_changes(
    edited_records: list[dict[str, Any]],
    original_records: list[dict[str, Any]],
    admin_mail: Optional[str] = None,
):
    admin_mail_q = urllib.parse.quote(admin_mail or "")
    resp = post(f"/certificates/apply-editor?admin_mail={admin_mail_q}", json={
        "edited": edited_records,
        "original": original_records,
    })
    return resp.get("reset_ids", [])

def get_admin_id(email: str):
    return get("/admins/id", params={"email": email})

def get_certificate_by_cert_number(cert_number: str):
    return get(f"/certificates/verify?cert_number={cert_number}")


