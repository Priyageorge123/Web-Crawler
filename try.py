import whisper
import os

model = whisper.load_model("base")
audio_file = "RCSS2-Jun-26-2024-0000Z.mp3"
result = model.transcribe(audio_file,fp16=False)
print(result["text"])
# Extract the base name of the audio file (without extension)
base_name = os.path.splitext(audio_file)[0]

# Create the output file name
output_file = f"{base_name}_transcription.txt"

# Write the transcription to the output file with UTF-8 encoding
with open(output_file, "w", encoding="utf-8") as file:
    file.write(result["text"])

print(f"Transcription saved to {output_file}")
