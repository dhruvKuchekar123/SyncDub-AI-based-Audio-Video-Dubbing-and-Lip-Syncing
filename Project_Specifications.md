# SyncDub: Project Objectives & Technical Specifications

SyncDub is a high-performance AI-driven video dubbing pipeline designed to automate the cross-lingual transformation of content with realistic visual synchronization. This document outlines the primary objectives and the production-ready toolset used in the current implementation.

---

## 🚀 Core Project Objectives

The project aims to solve the problem of language barriers in education and digital media through an automated, 5-stage pipeline:

### 1. Robust Automatic Speech Recognition (ASR)
- **Goal**: Implement high-accuracy transcription of Hindi speech using **OpenAI Whisper**, resilient to background noise and regional accents.
- **Accuracy**: Optimized for low WER (Word Error Rate) in Hindi speech.

### 2. Rapid Contextual Translation
- **Goal**: Perform high-speed Hindi-to-Marathi translation using **Deep-Translator**, grouping speech fragments into context-aware blocks for better grammatical flow.
- **Context**: Maintains semantic meaning across large paragraphs.

### 3. Neural Speech Synthesis (TTS)
- **Goal**: Generate natural-sounding Marathi speech using **Edge-TTS (Neural)**, leveraging high-fidelity voices that mirror human prosody and rhythm.
- **Quality**: Utilizes high-end cloud neural voices for stable and expressive output.

### 4. Intelligent Speaker Profiling
- **Goal**: Automatically match the generated voice (Aarohi/Manohar) to the original speaker's gender by analyzing median pitch frequencies using **Librosa**.
- **Automation**: Removes the need for manual voice selection.

### 5. Professional Lip Synchronization
- **Goal**: Re-animate the speaker's lip movements using **Wav2Lip** to perfectly match the generated Marathi audio track.
- **Precision**: Achieves frame-by-frame visual consistency.

### 6. Seamless End-to-End Pipeline
- **Goal**: Develop a scalable, asynchronous architecture using **FastAPI** that handles the transition from upload to final dubbed video automatically.

---

## 🛠️ Technical Stack (Implemented Models)

SyncDub integrates production-ready AI models across the entire pipeline:

| Pipeline Stage | Model / Tool | Functionality |
| :--- | :--- | :--- |
| **Speech-to-Text** | **OpenAI Whisper (Medium)** | Multi-lingual Hindi transcription. |
| **Translation** | **Deep-Translator** | High-speed API for Hindi-to-Marathi conversion. |
| **Speech Synthesis** | **Edge-TTS (Neural)** | Human-like Marathi voice generation. |
| **Speaker Profiling** | **Librosa** | Pitch-based frequency analysis and gender detection. |
| **Lip-Syncing** | **Wav2Lip** | Industry-standard lip animation. |
| **Backend / API** | **FastAPI** | Asynchronous service orchestration. |
| **Video Processing** | **MoviePy** | Audio extraction and video track merging. |

---

## 🏁 Future Scope
- **Offline Translation**: Transitioning to local models (like IndicTrans2) for full air-gapped security.
- **Voice Cloning**: Implementing zero-shot speaker embedding transfer (ECAPA-TDNN) for personalized synthesis.
- **Multi-Language Support**: Expanding the pipeline to support 10+ Indian regional languages.
