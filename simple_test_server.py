#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import torch
import numpy as np
import soundfile as sf
from flask import Flask, request, send_file
import io

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables for Apple Silicon
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

app = Flask(__name__)

# Global ChatTTS instance
chat = None

def init_chat():
    global chat
    if chat is not None:
        return chat
        
    print("Initializing ChatTTS...")
    try:
        from modules.repos_static.ChatTTS.ChatTTS import Chat
        
        chat = Chat()
        chat.load(source="custom", custom_path="./models/ChatTTS")
        print("✓ ChatTTS initialized successfully")
        return chat
    except Exception as e:
        print(f"✗ Failed to initialize ChatTTS: {e}")
        return None

@app.route('/test_tts')
def test_tts():
    text = request.args.get('text', 'Hello, this is a test.')
    
    # Initialize ChatTTS if needed
    chat_instance = init_chat()
    if chat_instance is None:
        return {"error": "ChatTTS not initialized"}, 500
    
    try:
        print(f"Generating audio for: {text}")
        
        # Create parameter objects
        refine_params = chat_instance.RefineTextParams(
            top_P=0.7,
            top_K=20,
            temperature=0.7
        )
        
        infer_params = chat_instance.InferCodeParams(
            prompt='[speed_5]',
            temperature=0.3,
            top_P=0.7,
            top_K=20
        )
        
        # Generate audio
        wavs = chat_instance.infer(
            texts=[text],
            params_refine_text=refine_params,
            params_infer_code=infer_params,
            use_decoder=True
        )
        
        if wavs is not None and len(wavs) > 0:
            # Convert to numpy and ensure correct data type
            audio_data = wavs[0]
            if isinstance(audio_data, torch.Tensor):
                audio_data = audio_data.cpu().numpy()
            
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Normalize if needed
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Create WAV file in memory
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, 24000, format='WAV')
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='audio/wav',
                as_attachment=True,
                download_name='generated_audio.wav'
            )
        else:
            return {"error": "No audio generated"}, 500
            
    except Exception as e:
        print(f"Error generating audio: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500

@app.route('/health')
def health():
    return {"status": "ok", "message": "Simple TTS server is running"}

if __name__ == '__main__':
    print("Starting simple TTS test server...")
    app.run(host='0.0.0.0', port=8080, debug=True) 