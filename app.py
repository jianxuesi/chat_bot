from flask import Flask, request, jsonify, render_template
import os
from flask_cors import CORS, cross_origin
import speech_recognition as sr 
from pydub import AudioSegment

r = sr.Recognizer()

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

# Create a folder to save uploaded audio files (if not exists)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    
    # Save the audio file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.wav')
    audio_file.save(file_path)

    """ Converts an audio file to WAV format if necessary """
    audio = AudioSegment.from_file(file_path)
    wav_path = file_path.rsplit(".", 1)[0] + ".wav"
    audio.export(wav_path, format="wav")

    text = ''
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)

        try:
            # Use Google Speech Recognition
            text = r.recognize_google(audio)
            print("Converted Speech:", text)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")

        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    # For demonstration, return the path of the uploaded file
    return jsonify({'message': 'Audio uploaded successfully', 'file_path': file_path, 'text': text}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5400)
