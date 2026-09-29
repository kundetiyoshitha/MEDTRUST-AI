document.addEventListener("DOMContentLoaded", () => {
    const voiceButton = document.getElementById("voiceButton");
    const responseBox = document.getElementById("aiResponse");

    if (!voiceButton || !responseBox) {
        console.warn("Voice elements not found.");
        return;
    }

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        voiceButton.addEventListener("click", () => {
            alert(
                "Voice input is not supported in this browser. " +
                "Please use Google Chrome or another browser with Speech Recognition support."
            );
        });

        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    let isListening = false;

    voiceButton.addEventListener("click", () => {
        if (isListening) {
            recognition.stop();
            return;
        }

        try {
            recognition.start();
        } catch (error) {
            console.error("Voice start error:", error);
        }
    });

    recognition.onstart = () => {
        isListening = true;

        voiceButton.classList.add("active");

        const originalText =
            voiceButton.dataset.originalText ||
            voiceButton.innerText;

        voiceButton.dataset.originalText = originalText;
        voiceButton.innerText = "🎙 Listening...";
    };

    recognition.onresult = event => {
        const transcript =
            event.results[0][0].transcript.trim();

        if (!transcript) return;

        const existingText = responseBox.value.trim();

        if (existingText) {
            responseBox.value =
                existingText + " " + transcript;
        } else {
            responseBox.value = transcript;
        }

        responseBox.dispatchEvent(new Event("input", {
            bubbles: true
        }));
    };

    recognition.onerror = event => {
        console.error("Voice recognition error:", event.error);

        if (event.error === "not-allowed") {
            alert(
                "Microphone permission was denied. " +
                "Please allow microphone access and try again."
            );
        } else if (event.error === "no-speech") {
            alert("No speech was detected. Please try again.");
        }
    };

    recognition.onend = () => {
        isListening = false;

        voiceButton.classList.remove("active");

        voiceButton.innerText =
            voiceButton.dataset.originalText ||
            "Voice Input";
    };

    console.log("MEDTRUST AI voice.js loaded successfully.");
});