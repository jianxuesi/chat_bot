from flask import Flask, request, jsonify, render_template, Response, send_file
import os
from flask_cors import CORS, cross_origin
import speech_recognition as sr 
from pydub import AudioSegment

import google.generativeai as genai

from gtts import gTTS
# from IPython.display import Audio

# recorder
r = sr.Recognizer()

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

# Create a folder to save uploaded audio files (if not exists)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# LLM
GOOGLE_API_KEY= "AIzaSyCEzH3-dchkGXkRq7b0oZMaksZLMkjem8A"
genai.configure(api_key=GOOGLE_API_KEY)
model_name = 'gemini-2.0-flash-exp' #@param ['gemini-1.5-flash', "gemini-1.5-flash-8b","gemini-1.5-flash-002","gemini-1.5-pro-002","gemini-2.0-flash-exp"]
model = genai.GenerativeModel(model_name)
prompt = "You are a japanese chatbot. Not matter which languarge user is typing. Always return in Japansese. Here is the user \nnew user input: \n{}  \n\nFormer conversation as Context: \n{}"
prompt2 = "You are a japanese languarge partner. Not matter which languarge user is saying. Always return in Japansese only. No need to include romaji or pronunciation in the return. Please chat like a japanese girl. If you want to know more about the user, feel free to ask questions if needed. Here is the user \nnew user input: \n{}  \n\nFormer conversation as Context: \n{}"
context = ""
user_input = ""

def chat_LLM(user_input, context):
  input = prompt2.format(user_input, context)
  response = model.generate_content(
    input
  )
  generated_text = response.text
  tts = gTTS(text=generated_text, lang="ja")
  tts_file = f"response.wav" #random filename
  tts.save(tts_file)
  return generated_text, tts_file

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
            text = r.recognize_google(audio, language="ja-JP")
            print("Converted Speech:", text)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")

        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    user_input = text
    global context
    generated_text, tts_file = chat_LLM(user_input, context)
    context += "user:" + user_input + "\n agent(self):" + generated_text + "\n"
    print("Chatbot Speech:", generated_text)
    # For demonstration, return the path of the uploaded file
    return jsonify({'message': 'Audio uploaded successfully', 'file_path': file_path, 'text': text}), 200

@app.route('/audio')
def stream_audio():
    def generate():
        with open("response.wav", "rb") as f:
            data = f.read(1024)
            while data:
                yield data
                data = f.read(1024)
    return Response(generate(), mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5400)
