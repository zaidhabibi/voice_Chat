import requests
import openai
import speech_recognition as sr
import pygame
import time
import os

class Conversation:

    def __init__(self):
        self.speech_recognition = sr.Recognizer()
        self.openai_key = self.open_file('openapikey.txt')
        self.eleven_key = self.open_file('elevenkey.txt')
        self.VOICES_URL = "https://api.elevenlabs.io/v1/voices"
        self.TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        self.voices = self.get_voices()
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"
        self.audio_counter = 1
        self.audio_folder_prefix = "chat_audio/chat_"
        self.headers = {
           "Content-Type": "application/json",
            "xi-api-key": self.eleven_key
        }
        self.mic = sr.Microphone()

       


    def create_body(self, text):
        body = {
            "text": text,
            "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
            }   
        }
        return body
    
    def open_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as infile:
            return infile.read()
    
    def gpt3_completion(self, prompt, engine='text-davinci-002', temp = 0.7, top_p = 1.0, tokens = 900, freq_pen = 0.0, pres_pen = 0.0, stop = ['<<END>>']):
        prompt = prompt.encode(encoding='ASCII', errors = 'ignore').decode()
        response = openai.Completion.create(
        engine = engine,
        prompt = prompt,
        temperature = temp,
        max_tokens = tokens,
        top_p = top_p,
        frequency_penalty = freq_pen,
        presence_penalty = pres_pen,
        stop = stop)
        text = response['choices'][0]['text'].strip()
        return text

    def create_audio_folder(self):
        if not os.path.exists("chat_audio"):
            os.makedirs("chat_audio")
            print("Directory chat_audio created")
    

    def get_voices(self):
        response = requests.get(self.VOICES_URL)
        return response.json()
    
    def initialize_playback(self):
        pygame.mixer.init()
        pygame.mixer.music.set_volume(1.0)
        
    def create_subfolder(self):
        for i in range(1, 1000):
            self.audio_folder = self.audio_folder_prefix + str(i)
            if not os.path.exists(self.audio_folder):
                os.makedirs(self.audio_folder)
                print(f"Directory {self.audio_folder} created")
                break
        
    def ask_user_speech(self):
        
        with self.mic as source:
            print("Speak now...")
            self.speech_recognition.adjust_for_ambient_noise(source)
            audio = self.speech_recognition.listen(source, timeout = 7)
            

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        
        try:
            response["transcription"] = self.speech_recognition.recognize_google(audio)
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"

        return response
    
    def get_response(self, body):
        # Convert text to speech
        return requests.post(self.TTS_URL.format(voice_id=self.voice_id), headers=self.headers, json=body)

    def play_audio_file(self):
         # Play audio file
        pygame.mixer.music.load(self.audio_file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        # Stop playback and release audio file
        pygame.mixer.music.stop()


    def conversation(self):
        self.audio_file_path = os.path.join(self.audio_folder, f"voice_output_{self.audio_counter}.mp3")
        while True:
            prompt = self.ask_user_speech()
            if prompt["success"]:
                break
            

        prompt = prompt["transcription"]
        
        gpt_response = self.gpt3_completion(prompt)
        print(gpt_response)

        body = self.create_body(gpt_response)
        response = self.get_response(body)
        self.initialize_playback()

        if response.status_code == 200:
            with open(self.audio_file_path, "wb") as f:
                f.write(response.content)
            self.play_audio_file()
        else:
            # Handle error
            print(f"Error {response.status_code}: {response.json()['detail']['msg']}")
    
    def delete_audio(self, audio_file):
        os.remove(audio_file)

if __name__ == "__main__":

    conversation = Conversation()
    conversation.create_subfolder()
    while True:
        
        openai.api_key = conversation.openai_key
        conversation.conversation()
        conversation.audio_counter += 1










    