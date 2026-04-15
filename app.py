from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mp
import textwrap
import os
import uuid
import requests
import numpy as np

app = Flask(__name__)

def criar_video(imagem_path, frase, output_path):
    img = Image.open(imagem_path).convert("RGB")
    
    # Redimensiona para formato 9:16
    img = img.resize((1080, 1920), Image.LANCZOS)
    
    draw = ImageDraw.Draw(img)
    
    # Fonte e tamanho
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    except:
        font = ImageFont.load_default()
    
    # Quebra o texto em linhas
    linhas = textwrap.wrap(frase, width=25)
    
    # Posição central
    y = img.height // 2 - (len(linhas) * 80) // 2
    
    for linha in linhas:
        bbox = draw.textbbox((0, 0), linha, font=font)
        w = bbox[2] - bbox[0]
        x = (img.width - w) // 2
        
        # Sombra preta
        draw.text((x+3, y+3), linha, font=font, fill=(0, 0, 0))
        # Texto branco
        draw.text((x, y), linha, font=font, fill=(255, 255, 255))
        y += 90
    
    # Salva frame
    frame_path = output_path.replace(".mp4", ".jpg")
    img.save(frame_path)
    
    # Cria vídeo de 5 segundos
    clip = mp.ImageClip(frame_path).set_duration(5)
    clip.write_videofile(output_path, fps=30, codec="libx264", audio=False)
    
    os.remove(frame_path)

@app.route("/criar-video", methods=["POST"])
def criar_video_endpoint():
    try:
        frase = request.form.get("frase", "")
        arquivo = request.files.get("imagem")
        
        if not frase or not arquivo:
            return jsonify({"erro": "Frase e imagem são obrigatórios"}), 400
        
        uid = str(uuid.uuid4())
        imagem_path = f"/tmp/{uid}_input.jpg"
        output_path = f"/tmp/{uid}_output.mp4"
        
        arquivo.save(imagem_path)
        
        criar_video(imagem_path, frase, output_path)
        
        os.remove(imagem_path)
        
        return send_file(output_path, mimetype="video/mp4", as_attachment=True, download_name="video.mp4")
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
