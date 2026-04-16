# v6
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import os, uuid, textwrap, re

app = Flask(__name__)

def separar_texto_emojis(frase):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F9FF"
        u"\U00002600-\U000027BF"
        u"\U0001FA00-\U0001FA6F"
        u"\U0001FA70-\U0001FAFF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE)
    emojis = emoji_pattern.findall(frase)
    texto_limpo = emoji_pattern.sub('', frase).strip()
    return texto_limpo, emojis

@app.route("/")
def health():
    return jsonify({"status": "ok", "versao": "6"})

@app.route("/criar-video", methods=["POST"])
def criar_video_endpoint():
    try:
        frase = request.form.get("frase", "")
        arquivo = request.files.get("imagem")
        if not frase or not arquivo:
            return jsonify({"erro": "Frase e imagem sao obrigatorios"}), 400
        uid = str(uuid.uuid4())
        imagem_path = f"/tmp/{uid}_input.jpg"
        output_path = f"/tmp/{uid}_output.jpg"
        arquivo.save(imagem_path)
        img = Image.open(imagem_path).convert("RGB")
        img = img.resize((1080, 1920), Image.LANCZOS)
        draw = ImageDraw.Draw(img)

        texto_limpo, emojis = separar_texto_emojis(frase)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
            font_emoji = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
            font_emoji = font

        linhas = textwrap.wrap(texto_limpo, width=22)
        total_linhas = len(linhas) + (1 if emojis else 0)
        y = img.height // 2 - (total_linhas * 95) // 2

        for linha in linhas:
            bbox = draw.textbbox((0, 0), linha, font=font)
            w = bbox[2] - bbox[0]
            x = (img.width - w) // 2
            draw.text((x+3, y+3), linha, font=font, fill=(0, 0, 0))
            draw.text((x, y), linha, font=font, fill=(255, 255, 255))
            y += 95

        if emojis:
            emoji_texto = ' '.join(emojis)
            bbox = draw.textbbox((0, 0), emoji_texto, font=font_emoji)
            w = bbox[2] - bbox[0]
            x = (img.width - w) // 2
            draw.text((x, y + 10), emoji_texto, font=font_emoji, fill=(255, 255, 255))

        img.save(output_path, quality=95)
        os.remove(imagem_path)
        return send_file(output_path, mimetype="image/jpeg", as_attachment=True, download_name="resultado.jpg")
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
