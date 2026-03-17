# SyncDub: AI-based Audio-Video Dubbing and Lip-Syncing

SyncDub is a sophisticated AI-powered pipeline designed to dub videos from Hindi to Marathi while maintaining realistic lip-syncing. It leverages state-of-the-art machine learning models to handle transcription, translation, speech synthesis, and visual synchronization.

## 🚀 Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (High-performance Python web API)
- **Speech-to-Text**: [OpenAI Whisper](https://github.com/openai/whisper) (Robust Hindi transcription)
- **Translation**: [Deep Translator](https://github.com/nidhaloff/deep-translator) (Hindi to Marathi translation)
- **Speech Synthesis**: [Edge TTS](https://github.com/rany2/edge-tts) (Natural sounding Marathi voice synthesis)
- **Lip-Syncing**: [Wav2Lip](https://github.com/Rudrabha/Wav2Lip) (Professional-grade lip-sync generation)
- **Audio Processing**: [Librosa](https://librosa.org/) (Pitch detection for gender matching) & [MoviePy](https://zulko.github.io/moviepy/)

### Frontend
- **Framework**: [React.js](https://reactjs.org/)
- **Communication**: [Axios](https://axios-http.com/) (Asynchronous API requests)

---

## 🛠️ Working Flow

The system follows a sequential multi-stage pipeline:

1. **Video Upload**: The user uploads a video file (Hindi speech) via the React frontend to the FastAPI backend.
2. **Audio Extraction**: The backend extracts the raw audio track from the video using MoviePy.
3. **Transcription**: OpenAI Whisper processes the audio to generate a text transcript in the source language (Hindi).
4. **Translation**: The Hindi text is translated into Marathi while preserving context and sentence structure.
5. **Pitch Analysis & Gender Detection**: Librosa analyzes the original audio's pitch to determine if the speaker is male or female.
6. **Natural Speech Synthesis**: Edge TTS generates a Marathi audio file using a neural voice that matches the detected gender (e.g., `mr-IN-AarohiNeural` or `mr-IN-ManoharNeural`).
7. **Wav2Lip Synchronization**: The system feeds the original video and the newly generated Marathi audio into Wav2Lip to synchronize the speaker's lip movements with the new audio.
8. **Final Rendering**: The dubbed video is merged and delivered back to the user for download/viewing.

---

## 📦 Installation & Setup

1. **Clone the Project**:
   ```bash
   git clone https://github.com/dhruvKuchekar123/SyncDub-AI-based-Audio-Video-Dubbing-and-Lip-Syncing.git
   ```

2. **Backend Setup**:
   - Install dependencies: `pip install -r requirements.txt`
   - Run Server: `python backend/server.py`

3. **Frontend Setup**:
   - Install packages: `cd frontend && npm install`
   - Run App: `npm start`

