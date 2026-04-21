"""
Sube el CV a Google Drive con la estructura correcta.
Carpeta: Asevia_2026-04-09
Archivo: cv-veronicaSerna-TechLeadAI.docx

Instalación (solo la primera vez):
  pip install google-auth-oauthlib google-api-python-client

Uso:
  python subir_cv_drive.py
"""

import os
from datetime import date
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
CV_PATH = "cv-veronicaSerna-TechLeadAI.docx"   # Ruta al CV en tu ordenador
EMPRESA = "Asevia"
FECHA   = date.today().strftime("%Y-%m-%d")     # 2026-04-09
FOLDER_NAME = f"{EMPRESA}_{FECHA}"             # Asevia_2026-04-09
CV_FILENAME = "cv-veronicaSerna-TechLeadAI.docx"
# ──────────────────────────────────────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/drive"]
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

def autenticar():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)
    return build("drive", "v3", credentials=creds)

def crear_carpeta(service, nombre):
    """Crea la carpeta en Drive (o la reutiliza si ya existe)."""
    res = service.files().list(
        q=f"name='{nombre}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()
    if res["files"]:
        folder_id = res["files"][0]["id"]
        print(f"Carpeta ya existente: {nombre} (id: {folder_id})")
    else:
        meta = {"name": nombre, "mimeType": "application/vnd.google-apps.folder"}
        folder = service.files().create(body=meta, fields="id").execute()
        folder_id = folder["id"]
        print(f"Carpeta creada: {nombre} (id: {folder_id})")
    return folder_id

def subir_cv(service, folder_id, cv_path, cv_filename):
    """Sube el CV a la carpeta indicada."""
    meta = {"name": cv_filename, "parents": [folder_id]}
    media = MediaFileUpload(cv_path, mimetype=MIME_DOCX, resumable=True)
    archivo = service.files().create(body=meta, media_body=media, fields="id, webViewLink").execute()
    print(f"\n✅ CV subido correctamente.")
    print(f"   Nombre:  {cv_filename}")
    print(f"   Carpeta: {FOLDER_NAME}")
    print(f"   Link:    {archivo.get('webViewLink')}")

if __name__ == "__main__":
    if not os.path.exists(CV_PATH):
        print(f"❌ No encuentro el archivo: {CV_PATH}")
        print("   Asegúrate de que el CV está en la misma carpeta que este script.")
    else:
        service = autenticar()
        folder_id = crear_carpeta(service, FOLDER_NAME)
        subir_cv(service, folder_id, CV_PATH, CV_FILENAME)
