#!/usr/bin/env python3
"""Sube un fichero a la carpeta FOLDER_CV_GENERADOS de Drive usando las
credenciales OAuth del .env de cv-server. Solo stdlib."""
import json
import mimetypes
import os
import sys
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

# cv-server es un repositorio hermano. Se puede reapuntar con CV_SERVER_ENV.
ENV = os.environ.get(
    "CV_SERVER_ENV", str(Path(__file__).resolve().parents[2] / "cv-server" / ".env")
)
FOLDER_DEFECTO = "1tHuVOIz3ratjRp8AmHsF0kGVpmy9DocY"


def leer_env(ruta):
    valores = {}
    with open(ruta, encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            valores[clave.strip()] = valor.strip().strip("'\"")
    return valores


def access_token(env):
    datos = urllib.parse.urlencode({
        "client_id": env["GOOGLE_CLIENT_ID"],
        "client_secret": env["GOOGLE_CLIENT_SECRET"],
        "refresh_token": env["GOOGLE_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    peticion = urllib.request.Request("https://oauth2.googleapis.com/token", data=datos)
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        return json.load(respuesta)["access_token"]


def subir(token, ruta, nombre, carpeta):
    tipo = mimetypes.guess_type(ruta)[0] or "application/octet-stream"
    with open(ruta, "rb") as fh:
        contenido = fh.read()

    frontera = uuid.uuid4().hex
    metadatos = json.dumps({"name": nombre, "parents": [carpeta]}).encode()
    cuerpo = b"".join([
        f"--{frontera}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode(),
        metadatos,
        f"\r\n--{frontera}\r\nContent-Type: {tipo}\r\n\r\n".encode(),
        contenido,
        f"\r\n--{frontera}--\r\n".encode(),
    ])

    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,webViewLink"
    peticion = urllib.request.Request(url, data=cuerpo, method="POST")
    peticion.add_header("Authorization", f"Bearer {token}")
    peticion.add_header("Content-Type", f"multipart/related; boundary={frontera}")
    with urllib.request.urlopen(peticion, timeout=120) as respuesta:
        return json.load(respuesta)


def main():
    ruta = sys.argv[1]
    nombre = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(ruta)
    env = leer_env(ENV)
    faltan = [c for c in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN") if not env.get(c)]
    if faltan:
        print(f"FALTAN CREDENCIALES: {', '.join(faltan)}")
        return 1
    carpeta = env.get("FOLDER_CV_GENERADOS", FOLDER_DEFECTO)
    resultado = subir(access_token(env), ruta, nombre, carpeta)
    print(f"OK id={resultado['id']}")
    print(f"LINK {resultado.get('webViewLink')}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.HTTPError as err:
        print(f"HTTPError {err.code}: {err.read().decode()[:500]}")
        sys.exit(1)
    except Exception as err:  # noqa: BLE001
        print(f"ERROR {type(err).__name__}: {err}")
        sys.exit(1)
