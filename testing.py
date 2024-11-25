import speech_recognition as sr

def synchronous_transcription():
    recognizer = sr.Recognizer()

    # Explicitly set the device index for the I2S microphone (card 0)
    mic = sr.Microphone(device_index=0)

    print("Adjusting microphone... Speak now!")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Start speaking for synchronous transcription. Press Ctrl+C to stop.")
    try:
        while True:
            with mic as source:
                # Capture small chunks of speech continuously
                print("Listening...")
                audio = recognizer.listen(source, timeout=100, phrase_time_limit=2)
                try:
                    # Transcribe the audio chunk immediately
                    text = recognizer.recognize_google(audio)
                    print(f"You said: {text}")
                except sr.UnknownValueError:
                    print("...")  # Display silence if nothing is understood
                except sr.RequestError as e:
                    print(f"API error: {e}")
    except KeyboardInterrupt:
        print("\nTranscription stopped.")

# Run the transcription function
synchronous_transcription()
