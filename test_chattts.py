#!/usr/bin/env python3
import os
import sys
import torch
import numpy as np
import soundfile as sf
from pathlib import Path

# Set environment variables for Apple Silicon
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_chattts():
    """Test ChatTTS basic functionality"""
    print("Testing ChatTTS on Apple Silicon...")
    
    # Check device availability
    if torch.backends.mps.is_available():
        device = "mps"
        print(f"✓ MPS device available")
    else:
        device = "cpu"
        print(f"Using CPU device")
    
    print(f"PyTorch version: {torch.__version__}")
    print(f"Device: {device}")
    
    try:
        # Import ChatTTS
        from modules.repos_static.ChatTTS.ChatTTS import Chat
        
        print("✓ ChatTTS imported successfully")
        
        # Initialize ChatTTS
        chat = Chat()
        print("✓ ChatTTS instance created")
        
        # Load models with experimental flag for MPS
        print("Loading ChatTTS models...")
        models_path = "./models/ChatTTS"
        
        # Use experimental=True for Apple Silicon
        if device == "mps":
            success = chat.load(
                source="custom", 
                custom_path=models_path,
                experimental=True
            )
        else:
            success = chat.load(
                source="custom", 
                custom_path=models_path
            )
            
        if success:
            print("✓ ChatTTS models loaded successfully")
        else:
            print("✗ Failed to load ChatTTS models")
            return False
            
        # Test text generation
        test_text = "你好，这是一个测试。"
        print(f"Testing with text: {test_text}")
        
        # Generate with basic settings
        try:
            # Use smaller batch size and ensure proper data types
            texts = [test_text]
            
            # Create parameter objects
            refine_params = chat.RefineTextParams(
                top_P=0.7,
                top_K=20,
                temperature=0.7
            )
            
            infer_params = chat.InferCodeParams(
                prompt='[speed_5]',
                temperature=0.3,
                top_P=0.7,
                top_K=20
            )
            
            # Generate audio
            print("Generating audio...")
            wavs = chat.infer(
                texts,
                use_decoder=True,
                params_refine_text=refine_params,
                params_infer_code=infer_params
            )
            
            if wavs is not None:
                print("✓ Audio generation successful")
                print(f"Generated audio type: {type(wavs)}")
                print(f"Generated audio shape: {wavs.shape if hasattr(wavs, 'shape') else 'No shape attribute'}")
                
                # Save test audio
                output_path = "test_output.wav"
                
                # Handle different return types
                if isinstance(wavs, list) and len(wavs) > 0:
                    audio_data = wavs[0]
                elif isinstance(wavs, np.ndarray):
                    # If it's a multi-dimensional array, take the first sample
                    if wavs.ndim > 1:
                        audio_data = wavs[0]
                    else:
                        audio_data = wavs
                elif isinstance(wavs, torch.Tensor):
                    audio_data = wavs.cpu().numpy()
                    if audio_data.ndim > 1:
                        audio_data = audio_data[0]
                else:
                    audio_data = wavs
                
                # Ensure audio is in the right format
                if isinstance(audio_data, torch.Tensor):
                    audio_data = audio_data.cpu().numpy()
                    
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32)
                    
                # Normalize if needed
                if np.max(np.abs(audio_data)) > 1.0:
                    audio_data = audio_data / np.max(np.abs(audio_data))
                
                sf.write(output_path, audio_data, 24000)
                print(f"✓ Audio saved to {output_path}")
                
                return True
            else:
                print("✗ No audio generated")
                return False
                
        except Exception as e:
            print(f"✗ Error during inference: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_device_compatibility():
    """Test device and data type compatibility"""
    print("\n=== Device Compatibility Test ===")
    
    # Test basic MPS functionality
    if torch.backends.mps.is_available():
        print("✓ MPS available")
        
        # Test basic tensor operations
        try:
            x = torch.randn(10, 10).to('mps')
            y = torch.randn(10, 10).to('mps')
            z = torch.mm(x, y)
            print("✓ Basic MPS tensor operations work")
        except Exception as e:
            print(f"✗ MPS tensor operations failed: {e}")
            
        # Test half precision
        try:
            x_half = torch.randn(10, 10, dtype=torch.float16).to('mps')
            y_half = torch.randn(10, 10, dtype=torch.float16).to('mps')
            z_half = torch.mm(x_half, y_half)
            print("✓ MPS half precision works")
        except Exception as e:
            print(f"✗ MPS half precision failed: {e}")
            
        # Test mixed precision
        try:
            x_half = torch.randn(10, 10, dtype=torch.float16).to('mps')
            x_float = x_half.float()
            print("✓ Half to float conversion works")
        except Exception as e:
            print(f"✗ Half to float conversion failed: {e}")
    else:
        print("✗ MPS not available")

if __name__ == "__main__":
    print("ChatTTS Apple Silicon Compatibility Test")
    print("=" * 50)
    
    # Test device compatibility first
    test_device_compatibility()
    
    print("\n=== ChatTTS Functionality Test ===")
    
    # Test ChatTTS
    success = test_chattts()
    
    if success:
        print("\n✓ All tests passed! ChatTTS is working on Apple Silicon.")
    else:
        print("\n✗ Tests failed. Need to investigate further.") 