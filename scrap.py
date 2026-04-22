import requests #para peticiones web
import tkinter as tk #crea interfaz gráfica
from tkinter import messagebox
from openpyxl import Workbook #crea los archivos excel
import os #manejo de carpetas y archivos


# ---------------------------
# 🔐 COOKIES (REEMPLAZA)
# ---------------------------
cookies = {
    "sessionid": "25964836367%3AWJbaRGGSHXWkMF%3A3%3AAYjtYX0vB3PektLsZhEZ8PuljwVr0G0WJ0QcBUfm9g",
    "csrftoken": "07OFJZR8mDhuh8Sc8OIAflTl0gIeKAr4"
}

# ---------------------------
# 🔧 HEADERS CORRECTOS
# ---------------------------
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "X-IG-App-ID": "936619743392459",
    "Referer": "https://www.instagram.com/",
    "Origin": "https://www.instagram.com"
}

# ---------------------------
# 📡 OBTENER INFO
# ---------------------------
def obtener_info(usuario):
    try:
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={usuario}"

        session = requests.Session()
        session.headers.update(headers)
        session.cookies.update(cookies)

        response = session.get(url)

        print("STATUS:", response.status_code)

        if response.status_code != 200:
            print("RESPUESTA:", response.text[:300])
            return None

        data = response.json()

        # ✅ VALIDACIÓN CORRECTA
        if "data" not in data or "user" not in data["data"]:
            print("Usuario no existe o error de acceso")
            return None

        user = data["data"]["user"]

        publicaciones = user["edge_owner_to_timeline_media"]["count"]
        seguidores = user["edge_followed_by"]["count"]
        seguidos = user["edge_follow"]["count"]

        posts = user["edge_owner_to_timeline_media"]["edges"]

        return publicaciones, seguidores, seguidos, posts
    except Exception as e:
        print("Error:", e)
        return None
# ---------------------------
# 📊 GUARDAR EXCEL
# ---------------------------
from datetime import datetime #fecha
def guardar_excel(usuario, datos):
    wb = Workbook()
    ws = wb.active

    ws.append(["Usuario", "Posts", "Seguidores", "Seguidos", "Fecha"])
    ws.append([usuario, datos[0], datos[1], datos[2], datetime.now()])

    wb.save(f"{usuario}_datos.xlsx")

# ---------------------------
# 🎯 BOTÓN
# ---------------------------
def ejecutar():
    usuario = entry.get()

    if not usuario:
        messagebox.showwarning("Error", "Ingresa usuario")
        return

    label.config(text="Procesando...")
    ventana.update()

    datos = obtener_info(usuario)

    if datos:
        guardar_excel(usuario, datos)

        label.config(text="✅ Completado")
        messagebox.showinfo("Listo", "Datos y publicaciones descargadas")
    else:
        label.config(text="❌ Error (revisa cookies)")

# ---------------------------
# 🖥️ INTERFAZ
# ---------------------------
ventana = tk.Tk()
ventana.title("Instagram Scraper (Cookies)")
ventana.geometry("400x250")

tk.Label(ventana, text="Usuario de Instagram").pack(pady=10)

entry = tk.Entry(ventana)
entry.pack()

tk.Button(ventana, text="Descargar", command=ejecutar).pack(pady=10)

label = tk.Label(ventana, text="")
label.pack()

ventana.mainloop()