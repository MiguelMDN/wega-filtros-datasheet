from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from PIL import Image
import io
import os

app = Flask(__name__)

def buscar_filtro(codigo):
    url = f"https://www.wegamotors.com/catalogo/busqueda?busqueda={codigo}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    try:
        img_tag = soup.find("img", {"class": "img-responsive"})
        img_url = img_tag["src"] if img_tag else None
        specs_tag = soup.find("ul", {"class": "caracteristicas"})
        specs = specs_tag.get_text(separator="\n") if specs_tag else "Sin especificaciones técnicas."
        nombre_tag = soup.find("h1")
        nombre = nombre_tag.text if nombre_tag else codigo
        return img_url, specs, nombre
    except Exception:
        return None, None, None

def crear_pdf(img_url, specs, nombre, codigo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Filtro WEGA: {nombre} ({codigo})", ln=True)
    # Imagen
    if img_url:
        try:
            img_resp = requests.get(img_url)
            img = Image.open(io.BytesIO(img_resp.content))
            img_path = f"temp_img_{codigo}.jpg"
            img.save(img_path)
            pdf.image(img_path, x=10, y=30, w=60)
            os.remove(img_path)
        except Exception:
            pdf.cell(0, 10, "Imagen no disponible.", ln=True)
    pdf.ln(65)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, specs)
    pdf_path = f"Filtro_{codigo}.pdf"
    pdf.output(pdf_path)
    return pdf_path

@app.route('/', methods=['GET', 'POST'])
def buscador():
    if request.method == 'POST':
        codigo = request.form['codigo']
        img_url, specs, nombre = buscar_filtro(codigo)
        if img_url and specs:
            pdf_path = crear_pdf(img_url, specs, nombre, codigo)
            return send_file(pdf_path, as_attachment=True)
        else:
            return render_template('buscador.html', error="Filtro no encontrado o datos insuficientes.")
    return render_template('buscador.html', error=None)

if __name__ == '__main__':
    app.run(debug=True)