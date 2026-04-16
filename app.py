# v4
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import os, uuid, textwrap

app = Flask(__name__)

@app.route("/")
def health():
    return jsonify({"status": "ok", "versao": "4"})

@app.route("/criar-video", methods=["POST"])
def criar_video_endpoint():
    try:
        frase = request.form.get("frase", "")
        arquivo = request.files.get("imagem")
        if not frase or not arquivo:
            return jsonify({"erro": "Frase e imagem sao obrigatorios"}), 400
        uid = str(uuid.uuid4())
        imagem_path = f"/tmp/{uid}.jpg"
        output_path = f"/tmp/{uid}.jpg"
        arquivo.save(imagem_path)
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
        img.save(output_path, quality=95)
        os.remove(imagem_path)
        return send_file(output_path, mimetype="image/jpeg", as_attachment=True, download_name="imagem.jpg")
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
