from typing import Any

import requests

from src.api.client import post, get


def import_csv_api(uploaded_file, institution, logo_file, template_type, template_file):
    if isinstance(uploaded_file, list):
        uploaded_file = uploaded_file[0]
    if isinstance(template_file, list):
        template_file = template_file[0]
    if isinstance(logo_file, list):
        logo_file = logo_file[0]

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "text/csv"
        ),
        "template_file": (
            template_file.name,
            template_file.getvalue(),
            "application/vnd.oasis.opendocument.text"
        )
    }

    if logo_file is not None:
        files["logo_file"] = (
            logo_file.name,
            logo_file.getvalue(),
            "image/png"
        )
    data = {
        "institution": institution,
        "template": template_type or "",
    }

    resp = post("/certificates/import-csv", files=files, data=data)

    return resp.json()


def generate_certificate(cert_number: str):
    resp = get("/certificates/generate-pdf", params={"cert_number": cert_number})
    return resp.content


def set_alias_email(email: str, alias: str):
    resp = post("/users/alias", json={
        "main_email": email,
        "alias_email": alias
    })
    return resp.json()


def get_certificates_for_user_email(email: str):
    resp = get("/certificates/by-user", params={"email": email})
    return resp.json()


def get_certificates_for_admin_email():
    resp = get("/certificates/by-admin")
    return resp.json()


def apply_certificate_editor_changes(
        edited_records: list[dict[str, Any]],
        original_records: list[dict[str, Any]],
):
    resp = post("/certificates/apply-editor", json={
        "edited": edited_records,
        "original": original_records,
    })
    return resp.json().get("reset_ids", [])


def get_admin_id(email: str):
    resp = get("/admins/id", params={"email": email})
    return resp.json()


def get_certificate_by_cert_number(cert_number: str):
    resp = get(f"/certificates/verify?cert_number={cert_number}")
    return resp.json()


def request_otp(email: str, role: str):
    try:
        resp = post("/auth/request-otp", json={"email": email, "role": role})
        return {"status": 200, **resp.json()}
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
    resp = post("/auth/verify-otp", json={"email": email, "role": role, "otp": otp})
    return resp.json()


def logout_api():
    resp = post("/auth/logout")
    return resp.json()


def check_existing_user(email: str, role: str):
    resp = get("/users/exists", params={"email": email, "role": role})
    return resp.json()


def check_admin_status(email: str, role: str):
    resp = get("/admins/status", params={"email": email, "role": role})
    return resp.json()


def create_admin(name: str, email: str, affiliation: str):
    resp = post("/admins/create", json={
        "name": name,
        "email": email,
        "affiliation": affiliation
    })
    return resp.json()


def send_admin_registration(to_email: str, email: str, name: str, affiliation: str, systemadmin_email: str):
    resp = post("/admins/register",
                json={"to_email": to_email, "email": email, "name": name, "affiliation": affiliation,
                      "systemadmin_email": systemadmin_email})
    return resp.json()
