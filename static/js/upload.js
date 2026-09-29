document.addEventListener("DOMContentLoaded", () => {
    const uploadButton = document.getElementById("uploadButton");
    const responseBox = document.getElementById("aiResponse");

    if (!uploadButton || !responseBox) {
        console.warn("Upload elements not found.");
        return;
    }

    const fileInput = document.createElement("input");

    fileInput.type = "file";
    fileInput.accept =
        ".txt,.md,.csv,.json,.pdf,.png,.jpg,.jpeg";
    fileInput.style.display = "none";

    document.body.appendChild(fileInput);

    uploadButton.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", async event => {
        const file = event.target.files[0];

        if (!file) return;

        const originalText =
            uploadButton.dataset.originalText ||
            uploadButton.innerText;

        uploadButton.dataset.originalText = originalText;
        uploadButton.innerText = "Uploading...";
        uploadButton.disabled = true;

        try {
            const extension =
                file.name.split(".").pop().toLowerCase();

            if (
                extension === "txt" ||
                extension === "md" ||
                extension === "csv" ||
                extension === "json"
            ) {
                const text = await file.text();

                if (!text.trim()) {
                    throw new Error(
                        "The selected file is empty."
                    );
                }

                responseBox.value = text;

                responseBox.dispatchEvent(
                    new Event("input", {
                        bubbles: true
                    })
                );

                showUploadMessage(
                    `✓ ${file.name} loaded successfully.`
                );

            } else if (extension === "pdf") {

                showUploadMessage(
                    "PDF selected. PDF text extraction needs to be connected to the backend."
                );

            } else if (
                extension === "png" ||
                extension === "jpg" ||
                extension === "jpeg"
            ) {

                showUploadMessage(
                    "Image selected. Image-to-text extraction needs to be connected to the document analysis pipeline."
                );

            } else {
                showUploadMessage(
                    "This file type is not supported."
                );
            }

        } catch (error) {
            console.error("Upload error:", error);

            showUploadMessage(
                error.message ||
                "Unable to read the selected file."
            );

        } finally {
            uploadButton.innerText =
                uploadButton.dataset.originalText ||
                "Upload";

            uploadButton.disabled = false;

            fileInput.value = "";
        }
    });

    function showUploadMessage(message) {
        let messageBox =
            document.getElementById("uploadStatusMessage");

        if (!messageBox) {
            messageBox = document.createElement("div");

            messageBox.id = "uploadStatusMessage";
            messageBox.className = "upload-status-message";

            responseBox.parentElement.appendChild(
                messageBox
            );
        }

        messageBox.textContent = message;

        clearTimeout(
            messageBox._hideTimer
        );

        messageBox._hideTimer = setTimeout(() => {
            messageBox.textContent = "";
        }, 5000);
    }

    console.log("MEDTRUST AI upload.js loaded successfully.");
});