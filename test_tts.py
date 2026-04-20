from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()

text = "नमस्कार, ही मराठी आवाज चाचणी आहे."

voice = texttospeech.VoiceSelectionParams(
    language_code="mr-IN",
    name="mr-IN-Wavenet-A"
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16
)

response = client.synthesize_speech(
    input=texttospeech.SynthesisInput(text=text),
    voice=voice,
    audio_config=audio_config
)

with open("test.wav", "wb") as f:
    f.write(response.audio_content)

print("✅ Marathi Wavenet TTS working")
