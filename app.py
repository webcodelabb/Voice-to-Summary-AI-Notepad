import gradio as gr
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# If you want to call an external FastAPI backend, set API_URL in your envvars
API_URL = os.getenv("API_URL", "")

def dummy_transcribe_and_summarize(audio):
    """Fallback placeholder function for local testing when no backend is available."""
    if not audio:
        return "No audio received.", "No summary generated."
    transcript = "[Transcript of the audio would appear here...]"
    summary = "[Summary of the transcript would appear here...]"
    return transcript, summary

def transcribe_and_summarize_remote(audio):
    """Send audio file to remote API for transcription and summarization."""
    if not API_URL:
        raise RuntimeError("API_URL not configured")
    if not audio:
        raise ValueError("No audio file provided")
    files = {"audio_file": ("audio.wav", open(audio, "rb"))}
    resp = requests.post(f"{API_URL}/transcribe", files=files, timeout=120)
    resp.raise_for_status()
    transcription = resp.json().get("transcription", "")

    resp2 = requests.post(f"{API_URL}/summarize", json={"text": transcription}, timeout=120)
    resp2.raise_for_status()
    summary = resp2.json().get("summary", "")
    return transcription, summary

def process_audio(audio):
    """Try remote API if configured, otherwise fallback to dummy function."""
    if API_URL:
        try:
            return transcribe_and_summarize_remote(audio)
        except Exception as e:
            # fallback to dummy but include error in summary for debugging
            transcript, summary = dummy_transcribe_and_summarize(audio)
            summary = f"[Remote API failed: {e}]\n\n" + summary
            return transcript, summary
    else:
        return dummy_transcribe_and_summarize(audio)


with gr.Blocks(title="Voice-to-Summary AI Notepad") as demo:
    gr.Markdown("""
    # � Voice-to-Summary AI Notepad
    Upload or record your voice, get instant transcripts and summaries.
    """)

    with gr.Row():
        audio_input = gr.Audio(source="microphone", type="filepath", label="Speak or upload an audio file")

    with gr.Row():
        transcript_output = gr.Textbox(label="Transcript", lines=6)
        summary_output = gr.Textbox(label="Summary", lines=6)

    submit_btn = gr.Button("Transcribe & Summarize")
    submit_btn.click(process_audio, inputs=[audio_input], outputs=[transcript_output, summary_output])


if __name__ == "__main__":
    demo.launch()