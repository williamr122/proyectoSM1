from flask import Flask, send_file, Response, render_template, request
import time
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')




@app.route('/video')
def video():
    return render_template('video.html')


@app.route('/video_chunk')
def video_chunk():
    def generate():
        with open("video.mp4", "rb") as f:
            chunk = f.read(1024 * 1024)
            while chunk:
                yield chunk
                time.sleep(1)
                chunk = f.read(1024 * 1024)
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
    app.run(host='127.0.0.1', port=5050)

if __name__ == '__main__':
    app.run()
