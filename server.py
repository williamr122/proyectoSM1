from flask import Flask, send_file, Response, render_template, request, url_for
import time
import matplotlib.pyplot as plt
import os
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video')
def video():
    return render_template('video.html')


@app.route('/video_chunk_page')
def video_chunk_page():
    return render_template('video_chunk.html')


@app.route('/video_chunk')
def video_chunk():
    def generate():
        filepath = os.path.join("static", "videos", "video.mp4")
        with open(filepath, "rb") as f:
            chunk_size = 1024 * 128  # 128 KB por chunk
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                time.sleep(0.5)  # Puedes ajustar para simular buffering
    return Response(generate(), mimetype='video/mp4')


@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        responses = {
            "preg1": request.form.get("preg1"),
            "preg2": request.form.get("preg2"),
            "preg3": request.form.get("preg3"),
            "preg4": request.form.get("preg4"),
            "preg5": request.form.get("preg5"),
            "preg6": request.form.get("preg6"),
            "preg7": request.form.get("preg7")
        }
        with open('survey_results.txt', 'a') as f:
            f.write(str(responses) + "\n")
        with open('ratings.txt', 'a') as rf:
            rf.write(f"{responses['preg6']}\n")
        return '¡Gracias por tu respuesta!'
    return render_template('survey.html')


@app.route('/metrics')
def metrics():
    try:
        with open('ratings.txt', 'r') as f:
            ratings = [int(line.strip()) for line in f.readlines() if line.strip().isdigit()]
        avg_rating = sum(ratings) / len(ratings)
    except:
        ratings = []
        avg_rating = 0

    plt.figure(figsize=(6,4))
    plt.hist(ratings, bins=range(1, 7), color='skyblue', edgecolor='black', align='left', rwidth=0.8)
    plt.title('Distribución de calificaciones QoE')
    plt.xlabel('Calificación (1-5)')
    plt.ylabel('Cantidad')
    plt.xticks(range(1, 6))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig('static/ratings_hist.png')
    plt.close()

    return f'<h3>Promedio MOS: {avg_rating:.2f}</h3><img src="/static/ratings_hist.png">'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

