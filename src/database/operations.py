import pandas as pd

from src.database.init_database import postgres
from util import Role


def set_alias_email(main_email: str, alias_email: str):
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET alias_email = %s
                WHERE main_email = %s
                """,
                (alias_email, main_email)
            )


def check_existing_user(email: str, role: str):
    with postgres() as con:
        with con.cursor() as cur:
            if role == Role.User:
                cur.execute(
                    """
                    SELECT 1
                    FROM users
                    WHERE main_email = %s
                       OR alias_email = %s
                    """,
                    (email, email)
                )
                user = cur.fetchone()
                if user:
                    return True

            if role == Role.Admin or role == Role.Registration:
                cur.execute(
                    """
                    SELECT 1
                    FROM admins
                    WHERE email = %s
                    """,
                    (email,)
                )
                admin = cur.fetchone()
                if admin:
                    return True
        return False


def create_admin(name: str, email: str, affiliation: str):
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                INSERT INTO admins (name, email, affiliation, created_at)
                VALUES (%s, %s, %s, NOW())
                """,
                (name, email, affiliation)
            )


def get_or_create_user_id(cur, main_email):
    cur.execute(
        "SELECT id FROM users WHERE main_email = %s",
        (main_email,)
    )
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO users (main_email, created_at)
        VALUES (%s, NOW()) RETURNING id;
        """,
        (main_email,)
    )
    return cur.fetchone()[0]


def get_admin_id(email: str):
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute(
                "SELECT id FROM admins WHERE email = %s",
                (email,)
            )
            row = cur.fetchone()
            if row:
                return row[0]
    return None


def get_user(cur, email: str):
    cur.execute(
        "SELECT id FROM users WHERE main_email = %s OR alias_email = %s",
        (email, email)
    )
    return cur.fetchone()[0]

def get_cert_template_path(cert_number: str):
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute(
                "SELECT template_path FROM certificates WHERE cert_number = %s",
                (cert_number,)
            )
            return cur.fetchone()[0]

def insert_csv(csv_file, institution, logo_path, admin_mail, template, template_path):
    with postgres() as con:
        with con.cursor() as cur:
            df = pd.read_csv(csv_file[0], sep=';')
            for _, row in df.iterrows():
                name = row['name']
                email = row['email']
                course_name = row['course_name']
                platform = row['platform']
                cert_number = row['cert_number']
                user_id = get_or_create_user_id(cur, email)
                admin_id = get_admin_id(admin_mail)
                cur.execute(
                    """
                    INSERT INTO certificates (name, email, course_name, platform, created_at, cert_number, institution, 
                                              template, template_path, logo_path, user_id, admin_id)
                    VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (name, email, course_name, platform, cert_number, institution, template, template_path,
                     logo_path, user_id, admin_id)
                )


def get_data_per_user(email: str):
    with postgres() as con:
        with con.cursor() as cur:
            user_id = get_user(cur, email)

            cur.execute("""
                        SELECT *
                        FROM certificates
                        WHERE user_id = %s
                        """,
                        (user_id,)
                        )
            return cur.fetchall()


def get_data_per_admin(email: str, as_df: bool = False):
    with postgres() as con:
        with con.cursor() as cur:
            admin_id = get_admin_id(email)

            cur.execute("""
                        SELECT *
                        FROM certificates
                        WHERE admin_id = %s
                        ORDER BY id ASC
                        """, (admin_id,))

            rows = cur.fetchall()

            if not as_df:
                return rows

            cols = [desc[0] for desc in cur.description]
            return pd.DataFrame(rows, columns=cols)

def get_data(as_df: bool = False):
    with postgres() as con:
        with con.cursor() as cur:

            cur.execute("""
                        SELECT *
                        FROM certificates
                        ORDER BY id ASC
                        """,)

            rows = cur.fetchall()

            if not as_df:
                return rows

            cols = [desc[0] for desc in cur.description]
            return pd.DataFrame(rows, columns=cols)


def verify_cert(cert_number: str):
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute("""
                        SELECT *
                        FROM certificates
                        WHERE cert_number = %s
                        """,
                        (cert_number,)
                        )
            return cur.fetchone()


def _none_if_nan(x):
    try:
        if pd.isna(x):
            return None
    except Exception:
        pass
    return x


def _split_changes(df_old: pd.DataFrame, df_new: pd.DataFrame, pk: str):
    df_old = df_old.copy()
    df_new = df_new.copy()

    old_ids = set(df_old[pk].dropna().tolist()) if not df_old.empty else set()
    new_ids = set(df_new[pk].dropna().tolist()) if not df_new.empty else set()

    deleted_ids = sorted(old_ids - new_ids)
    inserts = df_new[df_new[pk].isna()].copy()

    common_ids = sorted(old_ids & new_ids)
    if not common_ids:
        updates = df_new.iloc[0:0].copy()
        return inserts, updates, deleted_ids

    old = df_old.set_index(pk).loc[common_ids]
    new = df_new[df_new[pk].isin(common_ids)].set_index(pk).loc[common_ids]

    non_pk_cols = [c for c in df_new.columns if c != pk]

    changed_mask = pd.Series(False, index=common_ids)
    for c in non_pk_cols:
        a = old[c]
        b = new[c]
        changed_mask |= ~((a.isna() & b.isna()) | (a == b))

    updates = new.loc[changed_mask].reset_index()
    return inserts, updates, deleted_ids


def _validate_required_fields(df: pd.DataFrame):
    required_cols = ["name", "email", "course_name", "platform", "cert_number", "institution"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Fehlende Spalten im Editor: {', '.join(missing_cols)}")

    errors = []
    for i, row in df.iterrows():
        for col in required_cols:
            val = row.get(col)
            if val is None:
                errors.append((i, col))
                continue
            if isinstance(val, str) and val.strip() == "":
                errors.append((i, col))
                continue
            try:
                if pd.isna(val):
                    errors.append((i, col))
            except Exception:
                pass

    if errors:
        msg = "Pflichtfelder fehlen/leer in folgenden Zeilen (Editor-Index): "
        msg += ", ".join([f"[{i}] {c}" for i, c in errors[:25]])
        if len(errors) > 25:
            msg += f" … (+{len(errors) - 25} weitere)"
        raise ValueError(msg)


def _validate_unique_cert_number_in_editor(df: pd.DataFrame):
    dup_mask = df["cert_number"].astype(str).str.strip().duplicated(keep=False)
    if dup_mask.any():
        dup_vals = sorted(df.loc[dup_mask, "cert_number"].astype(str).str.strip().unique().tolist())
        raise ValueError(f"`cert_number` ist im Editor doppelt vorhanden: {', '.join(dup_vals[:20])}")


def _validate_cert_number_immutable(original_df: pd.DataFrame, edited_df: pd.DataFrame, pk: str = "id"):
    if original_df.empty:
        return
    if "cert_number" not in original_df.columns or "cert_number" not in edited_df.columns:
        return

    old = original_df.dropna(subset=[pk]).set_index(pk)
    new = edited_df.dropna(subset=[pk]).set_index(pk)

    common = old.index.intersection(new.index)
    if common.empty:
        return

    changed = []
    for cid in common:
        old_cn = str(old.loc[cid, "cert_number"]).strip()
        new_cn = str(new.loc[cid, "cert_number"]).strip()
        if old_cn != new_cn:
            changed.append(int(cid))

    if changed:
        raise ValueError(
            "`cert_number` darf bei bestehenden Zertifikaten nicht geändert werden. "
            f"Betroffene IDs: {', '.join(map(str, changed[:20]))}"
            + (" …" if len(changed) > 20 else "")
        )


def _validate_cert_number_unique_in_db(cur, edited_df: pd.DataFrame):
    certs = edited_df["cert_number"].astype(str).str.strip().tolist()
    certs = [c for c in certs if c]
    if not certs:
        return

    id_by_cert = {}
    if "id" in edited_df.columns:
        for _, r in edited_df.iterrows():
            cn = str(r.get("cert_number")).strip()
            rid = r.get("id")
            rid = None if (rid is None or (hasattr(pd, "isna") and pd.isna(rid))) else int(rid)
            id_by_cert[cn] = rid

    cur.execute(
        """
        SELECT id, cert_number
        FROM certificates
        WHERE cert_number = ANY (%s)
        """,
        (certs,)
    )
    rows = cur.fetchall()

    conflicts = []
    for db_id, db_cert in rows:
        db_cert = str(db_cert).strip()
        editor_id = id_by_cert.get(db_cert)

        if editor_id is not None and int(db_id) == int(editor_id):
            continue

        conflicts.append(db_cert)

    if conflicts:
        conflicts = sorted(set(conflicts))
        raise ValueError(
            "Diese `cert_number` existieren bereits in der DB und sind unique:\n"
            + ", ".join(conflicts[:20])
            + (" …" if len(conflicts) > 20 else "")
        )


from typing import Optional
import pandas as pd


def apply_certificate_editor_changes(
    edited_df: pd.DataFrame,
    original_df: pd.DataFrame,
    admin_mail: Optional[str] = None,
):
    PK = "id"

    sanitized_df, reset_ids = _enforce_cert_number_immutable(original_df, edited_df, pk=PK)

    _validate_required_fields(sanitized_df)
    _validate_unique_cert_number_in_editor(sanitized_df)

    inserts_df, updates_df, deleted_ids = _split_changes(original_df, sanitized_df, PK)

    if not inserts_df.empty and PK in inserts_df.columns:
        inserts_df = inserts_df.drop(columns=[PK])

    with postgres() as con:
        with con.cursor() as cur:
            admin_id = None
            if admin_mail is not None:
                admin_id = get_admin_id(admin_mail)
                if admin_id is None:
                    raise ValueError("Admin nicht gefunden.")

            _validate_cert_number_unique_in_db(cur, sanitized_df)

            if deleted_ids:
                if admin_id is not None:
                    cur.execute(
                        """
                        DELETE FROM certificates
                        WHERE admin_id = %s
                          AND id = ANY (%s)
                        """,
                        (admin_id, deleted_ids),
                    )
                else:
                    cur.execute(
                        """
                        DELETE FROM certificates
                        WHERE id = ANY (%s)
                        """,
                        (deleted_ids,),
                    )

            if not updates_df.empty:
                updatable_cols = [
                    "name",
                    "email",
                    "course_name",
                    "platform",
                    "institution",
                    "logo_path",
                ]

                for _, row in updates_df.iterrows():
                    cert_id = int(row["id"])
                    email = _none_if_nan(row.get("email"))

                    cur.execute(
                        "SELECT user_id FROM certificates WHERE id = %s",
                        (cert_id,),
                    )
                    existing_user_row = cur.fetchone()

                    if existing_user_row and existing_user_row[0] is not None:
                        user_id = existing_user_row[0]

                        if email is not None:
                            cur.execute(
                                """
                                UPDATE users
                                SET main_email = %s
                                WHERE id = %s
                                """,
                                (email, user_id),
                            )
                            cur.execute(
                                """
                                UPDATE certificates
                                SET email = %s
                                WHERE user_id = %s
                                """,
                                (email, user_id),
                            )
                    else:
                        user_id = get_or_create_user_id(cur, email)

                    sets = []
                    values = []

                    for col in updatable_cols:
                        if col in updates_df.columns:
                            sets.append(f"{col} = %s")
                            values.append(_none_if_nan(row.get(col)))

                    sets.append("user_id = %s")
                    values.append(user_id)

                    where_clause = "WHERE id = %s"
                    values.append(cert_id)

                    if admin_id is not None:
                        where_clause += " AND admin_id = %s"
                        values.append(admin_id)

                    cur.execute(
                        f"""
                        UPDATE certificates
                        SET {", ".join(sets)}
                        {where_clause}
                        """,
                        tuple(values),
                    )

            if not inserts_df.empty:
                for _, row in inserts_df.iterrows():
                    email = _none_if_nan(row.get("email"))
                    user_id = get_or_create_user_id(cur, email)

                    columns = [
                        "name",
                        "email",
                        "course_name",
                        "platform",
                        "created_at",
                        "cert_number",
                        "institution",
                        "user_id",
                        "logo_path",
                    ]
                    values = [
                        _none_if_nan(row.get("name")),
                        email,
                        _none_if_nan(row.get("course_name")),
                        _none_if_nan(row.get("platform")),
                        "NOW()",
                        _none_if_nan(row.get("cert_number")),
                        _none_if_nan(row.get("institution")),
                        user_id,
                        _none_if_nan(row.get("logo_path")),
                    ]

                    if admin_id is not None:
                        columns.append("admin_id")
                        values.append(admin_id)

                    placeholders = ["%s"] * (len(values) - 1) + [values[-1] if values[-1] == "NOW()" else "%s"]

                    cur.execute(
                        f"""
                        INSERT INTO certificates ({", ".join(columns)})
                        VALUES ({", ".join(placeholders)})
                        """,
                        tuple(v for v in values if v != "NOW()"),
                    )

    return reset_ids


def _enforce_cert_number_immutable(original_df: pd.DataFrame, edited_df: pd.DataFrame, pk: str = "id"):
    if original_df.empty:
        return edited_df.copy(), []

    if pk not in original_df.columns or pk not in edited_df.columns:
        return edited_df.copy(), []

    if "cert_number" not in original_df.columns or "cert_number" not in edited_df.columns:
        return edited_df.copy(), []

    df = edited_df.copy()
    reset_ids = []

    old = original_df.dropna(subset=[pk]).set_index(pk)

    existing_mask = df[pk].notna()
    for idx, row in df[existing_mask].iterrows():
        try:
            cid = int(row[pk])
        except Exception:
            continue

        if cid not in old.index:
            continue

        old_cn = old.loc[cid, "cert_number"]
        new_cn = row.get("cert_number")

        old_s = "" if old_cn is None else str(old_cn).strip()
        new_s = "" if new_cn is None else str(new_cn).strip()

        if old_s != new_s:
            df.at[idx, "cert_number"] = old_cn
            reset_ids.append(cid)

    reset_ids = sorted(set(reset_ids))
    return df, reset_ids
