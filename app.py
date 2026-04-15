from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import textwrap
import subprocess

app = Flask(__name__)

def criar_video(imagem_path, frase, output_path):
    img = Image.open(imagem_path).convert("RGB")
    img = img.resize((1080, 1920), Image.LANCZOS)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    except:
        font = ImageFont.load_default()

    linhas = textwrap.wrap(frase, width=25)
    y = img.height // 2 - (len(linhas) * 90) // 2

    for linha in linhas:
        bbox = draw.textbbox((0, 0), linha, font=font)
        w = bbox[2] - bbox[0]
        x = (img.width - w) // 2
        draw.text((x+3, y+3), linha, font=font, fill=(0, 0, 0))
        draw.text((x, y), linha, font=font, fill=(255, 255, 255))
        y += 90

    frame_path = output_path.replace(".mp4", ".jpg")
    img.save(frame_path)

    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", frame_path,
        "-t", "5",
        "-vf", "scale=1080:1920",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ], check=True)

    os.remove(frame_path)

@app.route("/criar-video", methods=["POST"])
def criar_video_endpoint():
    try:
        frase = request.form.get("frase", "")
        arquivo = request.files.get("imagem")

        if not frase or not arquivo:
            return jsonify({"erro": "Frase e imagem sao obrigatorios"}), 400

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
