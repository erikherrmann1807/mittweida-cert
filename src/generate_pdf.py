import zipfile
import shutil
from pathlib import Path
import subprocess
import tempfile

SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"


def convert_odt_to_pdf(template_path, placeholders, soffice_path=SOFFICE_PATH):
    template_path = Path(template_path).resolve()

    soffice_exe = Path(soffice_path)
    if not soffice_exe.exists():
        raise FileNotFoundError(
            f"LibreOffice (soffice.exe) nicht gefunden unter:\n  {soffice_exe}\n"
            f"Bitte den Pfad in SOFFICE_PATH im Skript anpassen."
        )

    temp_dir = Path(tempfile.mkdtemp())
    try:
        temp_odt = temp_dir / "temp.odt"

        with zipfile.ZipFile(template_path, 'r') as zIn, \
             zipfile.ZipFile(temp_odt, 'w', zipfile.ZIP_DEFLATED) as zOut:

            for item in zIn.infolist():
                data = zIn.read(item.filename)

                if item.filename == "content.xml":
                    text = data.decode("utf-8")
                    for placeholder, value in placeholders.items():
                        text = text.replace(placeholder, value)
                    data = text.encode("utf-8")

                zOut.writestr(item, data)

        cmd = [
            str(soffice_exe),
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(temp_dir),
            str(temp_odt)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print("Fehler beim PDF-Export:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            raise RuntimeError("LibreOffice-Export fehlgeschlagen")

        temp_pdf = temp_dir / f"{temp_odt.stem}.pdf"
        if not temp_pdf.exists():
            raise FileNotFoundError(f"Erwartete PDF nicht gefunden: {temp_pdf}")

        pdf_bytes = temp_pdf.read_bytes()
        return pdf_bytes

    finally:
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            pass