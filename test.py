# from google.cloud import texttospeech 
from moviepy.editor import VideoFileClip


# client = texttospeech.TextToSpeechClient()
# voices = client.list_voices()

# print("Available Marathi Voices:")
# for v in voices.voices:
#     if "mr" in v.language_codes[0]:
#         print(f"- {v.name} ({v.ssml_gender})")

# # Synthesize test audio
# text = "नमस्कार, हे एक चाचणी ऑडिओ आहे."
# voice = texttospeech.VoiceSelectionParams(language_code="mr-IN", ssml_gender=texttospeech.SsmlVoiceGender.MALE)
# audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
# synthesis_input = texttospeech.SynthesisInput(text=text)
# response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
# with open("test_output.mp3", "wb") as out:
#     out.write(response.audio_content)
# print("✅ Audio file 'test_output.mp3' created successfully!")
