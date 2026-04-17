# v7
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import os, uuid, textwrap, re

app = Flask(__name__)

def remover_emojis(texto):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F9FF"
        u"\U00002600-\U000027BF"
        u"\U0001FA00-\U0001FA6F"
        u"\U0001FA70-\U0001FAFF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', texto).strip()

@app.route("/")
def health():
    return jsonify({"status": "ok", "versao": "7"})

@app.route("/criar-video", methods=["POST"])
def criar_video_endpoint():
    try:
        frase = request.form.get("frase", "")
        arquivo = request.files.get("imagem")
        if not frase or not arquivo:
            return jsonify({"erro": "Frase e imagem sao obrigatorios"}), 400

        frase = remover_emojis(frase)

        uid = str(uuid.uuid4())
        imagem_path = f"/tmp/{uid}_input.jpg"
        output_path = f"/tmp/{uid}_output.jpg"
        arquivo.save(imagem_path)

        img = Image.open(imagem_path).convert("RGB")
        # Mantém proporção e adiciona fundo preto
        img_original = img.copy()
        img = Image.new("RGB", (1080, 1920), (0, 0, 0))
        img_original.thumbnail((1080, 1920), Image.LANCZOS)
        x = (1080 - img_original.width) // 2
        y = (1920 - img_original.height) // 2
        img.paste(img_original, (x, y))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 55)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
            except:
                font = ImageFont.load_default()

        linhas = textwrap.wrap(frase, width=28)
        y = img.height // 2 - (len(linhas) * 70) // 2

        for linha in linhas:
            bbox = draw.textbbox((0, 0), linha, font=font)
            w = bbox[2] - bbox[0]
            x = (img.width - w) // 2
            # Sombra
            draw.text((x+3, y+3), linha, font=font, fill=(0, 0, 0))
            # Texto branco
            draw.text((x, y), linha, font=font, fill=(255, 255, 255))
            y += 70

        img.save(output_path, quality=95)
        os.remove(imagem_path)
        return send_file(output_path, mimetype="image/jpeg", as_attachment=True, download_name="resultado.jpg")
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
