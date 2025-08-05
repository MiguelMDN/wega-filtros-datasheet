import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from PIL import Image
import io

# Función para buscar el filtro en la web
def buscar_filtro(codigo):
    url = f"https://www.wegamotors.com/catalogo/busqueda?busqueda={codigo}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Extraer imagen y especificaciones técnicas
    try:
        img_url = soup.find("img", {"class": "img-responsive"})["src"]
        specs = soup.find("ul", {"class": "caracteristicas"}).get_text(separator="\n")
        nombre = soup.find("h1").text
        return img_url, specs, nombre
    except Exception as e:
        return None, None, None

# Función para crear el PDF
def crear_pdf(img_url, specs, nombre, codigo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Filtro WEGA: {nombre} ({codigo})", ln=True)
    # Descargar y agregar imagen
    img_resp = requests.get(img_url)
    img = Image.open(io.BytesIO(img_resp.content))
    img.save("temp_img.jpg")
    pdf.image("temp_img.jpg", x=10, y=30, w=60)
    pdf.ln(65)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, specs)
    pdf.output(f"Filtro_{codigo}.pdf")
    return f"Filtro_{codigo}.pdf"

# GUI
def buscar():
    codigo = entry_codigo.get()
    img_url, specs, nombre = buscar_filtro(codigo)
    if img_url and specs:
        pdf_path = crear_pdf(img_url, specs, nombre, codigo)
        messagebox.showinfo("PDF Generado", f"PDF creado: {pdf_path}")
    else:
        messagebox.showerror("Error", "Filtro no encontrado.")

root = tk.Tk()
root.title("Buscador de Filtros WEGA")

tk.Label(root, text="Código del filtro WEGA:").pack()
entry_codigo = tk.Entry(root)
entry_codigo.pack()

tk.Button(root, text="Buscar y generar PDF", command=buscar).pack()

root.mainloop()