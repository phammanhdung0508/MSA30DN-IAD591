import whisper

print("Loading model...")
model = whisper.load_model("base")  # tiny / base / small

print("Transcribing...")
result = model.transcribe("record.wav", language="vi")

print("========== RESULT ==========")
print(result["text"])
