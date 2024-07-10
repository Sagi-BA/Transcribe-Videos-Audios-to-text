import os
from moviepy.editor import AudioFileClip
from gradio_client import Client, file
import time

class GradioClientWrapper:
    def __init__(self, client_name='benderrodriguez/transcribe'):
        self.client = Client(client_name)

    def transcribe_audio(self, audio_file_paths, chunk_duration_minutes=25, api_name="/transcribe"):
        all_transcriptions = {}
        
        for audio_file_path in audio_file_paths:
            transcriptions = []
            try:
                # Load the audio file
                audio = AudioFileClip(audio_file_path)
                duration_seconds = audio.duration
                chunk_duration_seconds = chunk_duration_minutes * 60
                
                num_chunks = int(duration_seconds // chunk_duration_seconds) + 1
                chunk_dir = "audio_chunks"
                os.makedirs(chunk_dir, exist_ok=True)

                for chunk_idx in range(num_chunks):
                    start_time = chunk_idx * chunk_duration_seconds
                    end_time = min((chunk_idx + 1) * chunk_duration_seconds, duration_seconds)
                    chunk = audio.subclip(start_time, end_time)
                    
                    chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_idx}.mp3")
                    chunk.write_audiofile(chunk_path)
                    
                    # Retry logic
                    retries = 3
                    for attempt in range(retries):
                        try:
                            result = self.client.predict(
                                audio_file=file(chunk_path),
                                api_name=api_name
                            )
                            transcriptions.append(result)
                            break
                        except Exception as e:
                            print(f"Attempt {attempt + 1} failed: {e}")
                            time.sleep(2)  # Wait for 2 seconds before retrying
                    else:
                        print(f"Failed to transcribe chunk {chunk_idx + 1} of {audio_file_path} after {retries} attempts.")
                        transcriptions.append(None)

                # Clean up the temporary chunk files
                for chunk_file in os.listdir(chunk_dir):
                    os.remove(os.path.join(chunk_dir, chunk_file))
                os.rmdir(chunk_dir)
                
            except Exception as e:
                print(f"An error occurred during transcription of {audio_file_path}: {e}")
            
            print(transcriptions)
            all_transcriptions[audio_file_path] = transcriptions
        
        return all_transcriptions

# Example usage
if __name__ == "__main__":
    client_wrapper = GradioClientWrapper()
    audio_file_paths = [os.path.join("uploads", "iris bar on_small.mp3"),
                        os.path.join("uploads", "טרופותי _ סיפורים לפני השינה _ שעת סיפור לילדים _ סיפור טרופותי _ The Gruffalo.mp4")]
    for audio_file_path in audio_file_paths:
        if not os.path.exists(audio_file_path):
            print(f"File not found: {audio_file_path}")

    results = client_wrapper.transcribe_audio(audio_file_paths)
    for file_path, transcriptions in results.items():
        if transcriptions:
            for idx, result in enumerate(transcriptions):
                print(f"Transcription for {file_path} chunk {idx+1}:")
                print(result)
        else:
            print(f"Transcription failed for {file_path}.")
