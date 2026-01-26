from typing import Any

import requests

from src.api.client import post, get


def create_admin(name: str, email: str, affiliation: str):
    return post("/admins/create", json={
        "name": name,
        "email": email,
        "affiliation": affiliation,
    })


def import_csv_api(uploaded_file, institution, logo_path, template_type, template_path):
    if isinstance(uploaded_file, list):
        uploaded_file = uploaded_file[0]

    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")
    }
    data = {
        "institution": institution,
        "logo_path": logo_path or "",
        "template": template_type or "",
        "template_path": template_path or "",
    }

    return post("/certificates/import-csv", files=files, data=data)


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


def get_certificates_for_admin_email():
    return get("/certificates/by-admin")


def apply_certificate_editor_changes(
        edited_records: list[dict[str, Any]],
        original_records: list[dict[str, Any]],
):
    resp = post("/certificates/apply-editor", json={
        "edited": edited_records,
        "original": original_records,
    })
    return resp.get("reset_ids", [])


def get_admin_id(email: str):
    return get("/admins/id", params={"email": email})


def get_certificate_by_cert_number(cert_number: str):
    return get(f"/certificates/verify?cert_number={cert_number}")


def request_otp(email: str, role: str):
    try:
        resp = post("/auth/request-otp", json={"email": email, "role": role})
        return {"status": 200, **resp}
    except requests.HTTPError as e:
        r = e.response
        if r is not None and r.status_code == 429:
            try:
                payload = r.json()
            except Exception:
                payload = {}
            return {"status": 429, **payload}
        raise


def verify_otp(email: str, role: str, otp: str):
    return post("/auth/verify-otp", json={"email": email, "role": role, "otp": otp})


def logout_api():
    return post("/auth/logout")


def check_existing_user(email: str, role: str):
    return post(f"/users/exists?email={email}&role={role}")
