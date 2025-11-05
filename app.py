import gradio as gr
import requests
import json
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the API URL (change this when deploying to Spaces)
API_URL = os.getenv("API_URL", "http://localhost:8000")

def transcribe_and_summarize(audio):
    """
    Process audio file through the API for transcription and summarization
    """
    try:
        # First, transcribe the audio
        files = {"audio_file": ("audio.wav", open(audio, "rb"))}
        transcribe_response = requests.post(
            f"{API_URL}/transcribe",
            files=files
        )
        transcribe_response.raise_for_status()
        transcription = transcribe_response.json().get("transcription", "")
        
        # Then, get the summary
        summary_response = requests.post(
            f"{API_URL}/summarize",
            json={"text": transcription}
        )
        summary_response.raise_for_status()
        summary = summary_response.json().get("summary", "")
        
        return transcription, summary
    except Exception as e:
        return str(e), str(e)

# Create the Gradio interface
with gr.Blocks(title="Voice-to-Summary AI Notepad") as demo:
    gr.Markdown(
        """
    # 🎙️ Voice-to-Summary AI Notepad
    
    Upload an audio file to get its transcription and a concise summary.
    """
    )
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                label="Upload Audio",
                type="filepath"
            )
            submit_btn = gr.Button("Transcribe & Summarize", variant="primary")
        
        with gr.Column():
            transcription_output = gr.Textbox(
                label="Transcription",
                lines=10,
                placeholder="Transcription will appear here..."
            )
            summary_output = gr.Textbox(
                label="Summary",
                lines=5,
                placeholder="Summary will appear here..."
            )
    
    # Set up the click event
    submit_btn.click(
        fn=transcribe_and_summarize,
        inputs=[audio_input],
        outputs=[transcription_output, summary_output]
    )
    
    gr.Markdown(
        """
    ### How to use:
    1. Upload an audio file (supported formats: WAV, MP3, M4A)
    2. Click the "Transcribe & Summarize" button
    3. Wait for both the transcription and summary to appear
    
    Note: Processing time may vary depending on the length of the audio file.
    """
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()