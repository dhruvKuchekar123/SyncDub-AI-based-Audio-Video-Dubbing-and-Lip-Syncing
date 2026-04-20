# SyncDub: Competition Demonstration Guide

This guide provides a structured script, demonstration flow, and technical backup for your online project competition.

---

## 1. Physical & Technical Setup (Pre-Demo)

> [!IMPORTANT]
> **Don't rely on live processing for everything!** Heavy AI models (Whisper/Wav2Lip) can take several minutes to run, which is too long for a 5-10 minute presentation.

- **Pre-recorded Clips**: Have 3 folders ready on your desktop:
  1. `Input`: The original Hindi video.
  2. `Processing`: Screenshots/short clips of the terminal running or the frontend progress bar (to show it's real).
  3. `Output`: 2-3 high-quality dubbed Marathi videos (one male, one female).
- **Environment**: Ensure your backend server is running (`python server.py`) and your frontend is active.
- **Screen Sharing**: Use "Share System Audio" when showing the final output so the judges can hear the dubbing quality.

---

## 2. The Pitch Script (Timing: 3-5 Minutes)

### Phase 1: The Hook & Problem (30-45 Seconds)
"Hello judges, in a country like India with 22 official languages, the biggest barrier to education and entertainment is **language access**. Thousands of Hindi educational videos are locked away from Marathi-speaking students because of the high cost of professional dubbing. We present **SyncDub**—an AI-driven pipeline that doesn't just translate, but transforms content across languages with perfect lip-syncing."

### Phase 2: The Solution (30 Seconds)
"SyncDub is a fully automated, cross-lingual dubbing engine. It takes a Hindi video, understands the speech, translates it to Marathi while maintaining the speaker's gender and natural prosody, and finally—re-animates the speaker's lips to match the new language perfectly."

### Phase 3: The Live Demo (1-2 Minutes)
*Start sharing your screen now.*
1. **Show the original**: "Here is our input—a standard Hindi speech video." (Play 5 seconds).
2. **Show the Frontend**: "We upload it to our SyncDub dashboard. Our system immediately starts the pipeline."
3. **The 'Magic' Reveal**: "Since the process takes time, I have the final output here." (Play the Marathi dubbed video).
4. **Point out details**: "Notice how the voice of the speaker matches the original gender, and the lip movements are completely synchronized with the Marathi syllables."

### Phase 4: Technical Deep-Dive (45 Seconds)
"Under the hood, we use a sophisticated 5-step pipeline:
1. **ASR (Speech-to-Text)**: OpenAI Whisper transcribes Hindi speech with high precision.
2. **Contextual Translation**: We group segments into blocks for better Marathi grammar.
3. **Intelligent Speaker Profiling**: We use **Librosa** for pitch-based gender detection to auto-select the right voice.
4. **Neural TTS**: **Edge-TTS** generates human-like Marathi audio.
5. **Lip-Sync Visualization**: **Wav2Lip** re-renders the video frames to match the new audio track."

### Phase 5: Future Scope & Conclusion (30 Seconds)
"SyncDub isn't just for Marathi—it's built to be modular. We can expand to 10+ Indian regional languages soon. Our goal is to make content democratization as easy as a single 'Upload' button. Thank you, and we are open for questions!"

---

## 3. Demonstration Flow (Step-by-Step)

| Step | Action | What to say |
| :--- | :--- | :--- |
| **Step 1** | Open Frontend | "This is our clean, user-friendly interface." |
| **Step 2** | Click Upload | "I'm uploading a 10-second Hindi clip. The system triggers the backend pipeline." |
| **Step 3** | Show Progress | "You can see the progress bar updating: Transcription... Translation... Lipsyncing." |
| **Step 4** | Play Output | "And here is the final result. Listen to the Marathi pronunciation." |
| **Step 5** | Compare | "Compare the original lips vs the dubbed lips. The sync is frame-perfect." |

---

## 4. Expected Technical Questions (Q&A)

> [!TIP]
> **Prepare for these common 'Trap' questions from judges:**

**Q1: How do you handle different genders?**
*   **Answer**: "We implemented a pitch-analysis component using Librosa's `pyin` algorithm. It calculates the median frequency of the original voice. If it's above 160Hz, the system automatically selects a female Marathi voice; otherwise, it uses a male voice."

**Q2: Translation often loses context. How do you solve that?**
*   **Answer**: "Unlike simple line-by-line translation, SyncDub groups short speech segments into larger blocks or 'context paragraphs' before sending them to the translator. This preserves the grammatical flow of Marathi."

**Q3: How much time does it take for a 1-minute video?**
*   **Answer**: "In a single CPU environment, it takes about 3-5 minutes. With a dedicated GPU, we can achieve near real-time performance of 1.5x the video length."

**Q4: Why Wav2Lip?**
*   **Answer**: "Wav2Lip is state-of-the-art because it is 'speaker-independent'. It works on any face, regardless of the person's identity or language, making it perfect for a general-purpose dubbing tool."

---

## 5. Pro-Tips for Online Competitions
1. **Blur your Background**: Keeps focus on you.
2. **Tab Management**: Close unrelated tabs. Have only your demo and script open.
3. **Sound Check**: Use a good microphone. The judges need to hear the *quality* of your AI voice.
4. **Conclusion Slide**: End with a slide that has your **Contact Info** and **Github Repo Link**.
