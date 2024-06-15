import speech_recognition as sr
import pyaudio
from better_profanity import profanity
import requests
import json


# Function to send HTTP request with JSON data to server
def send_data_to_server(data):
    url = "http://localhost:8080/process-data"  # Replace with your server's URL and endpoint
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    print("HTTP Response:", response.status_code)
    print("HTTP Response:", response.status_code)


# Function to create json file
def create_json_file(word):
    data = {"unusual_word": word}
    with open("unusual_word.json", "w") as file:
        json.dump(data, file)


# Function to listen for speech using the microphone
def listen_for_speech():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text.lower(), audio.get_raw_data()
    except sr.UnknownValueError:
        return "", audio.get_raw_data()


# Function to detect curse words in the text
def detect_curses(text):
    words = text.split()
    detected_curses = [word for word in words if profanity.contains_profanity(word)]
    return detected_curses if detected_curses else None


# Main function
def main():
    # Initialize PyAudio for audio capture
    audio_format = pyaudio.paInt16
    channels = 1
    chunk = 2048
    rate = 22050

    p = pyaudio.PyAudio()
    stream = p.open(format=audio_format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    try:
        while True:
            # Capture audio data and recognized text
            text, audio_data = listen_for_speech()

            if text:
                # Print the entire recognized text
                # print("Recognized text:", text)

                # Detect curses
                curses = detect_curses(text)
                if curses:
                    print("Curse word(s) detected:", curses)
                    create_json_file(curses)
                    send_data_to_server({"event": "curse_word_detected", "word": curses})

    except KeyboardInterrupt:
        # Cleanup when program is interrupted
        print("Exiting...")
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    main()
