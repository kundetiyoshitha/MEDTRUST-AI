document.addEventListener("DOMContentLoaded", () => {
    const cameraButton = document.getElementById("cameraButton");

    if (!cameraButton) {
        console.warn("Camera button not found.");
        return;
    }

    let stream = null;

    function createCameraModal() {
        const modal = document.createElement("div");

        modal.id = "medtrustCameraModal";

        modal.innerHTML = `
            <div class="camera-overlay">
                <div class="camera-modal">
                    <div class="camera-header">
                        <div>
                            <span class="camera-eyebrow">
                                MEDTRUST AI
                            </span>
                            <h3>Camera Input</h3>
                        </div>

                        <button
                            type="button"
                            class="camera-close"
                            id="closeCameraButton"
                        >
                            ×
                        </button>
                    </div>

                    <div class="camera-preview-wrapper">
                        <video
                            id="cameraVideo"
                            autoplay
                            playsinline
                        ></video>

                        <canvas
                            id="cameraCanvas"
                            style="display:none;"
                        ></canvas>
                    </div>

                    <div
                        id="cameraMessage"
                        class="camera-message"
                    >
                        Position the document clearly inside the frame.
                    </div>

                    <div class="camera-actions">
                        <button
                            type="button"
                            id="captureCameraButton"
                            class="primary-button"
                        >
                            📷 Capture
                        </button>

                        <button
                            type="button"
                            id="cancelCameraButton"
                            class="secondary-button"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        return modal;
    }

    async function openCamera() {
        const modal = createCameraModal();

        const video = modal.querySelector("#cameraVideo");
        const closeButton = modal.querySelector("#closeCameraButton");
        const cancelButton = modal.querySelector("#cancelCameraButton");
        const captureButton = modal.querySelector("#captureCameraButton");
        const message = modal.querySelector("#cameraMessage");

        try {
            if (!navigator.mediaDevices ||
                !navigator.mediaDevices.getUserMedia) {

                throw new Error(
                    "Camera access is not supported by this browser."
                );
            }

            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: "environment"
                },
                audio: false
            });

            video.srcObject = stream;

            message.textContent =
                "Camera ready. Capture the document when it is clear.";

        } catch (error) {
            console.error("Camera error:", error);

            message.textContent =
                "Unable to access the camera. Please allow camera permission and try again.";

            captureButton.disabled = true;
        }

        closeButton.addEventListener("click", closeCamera);
        cancelButton.addEventListener("click", closeCamera);

        captureButton.addEventListener("click", () => {
            captureImage(video, modal);
        });

        modal.addEventListener("click", event => {
            if (event.target === modal.querySelector(".camera-overlay")) {
                closeCamera();
            }
        });
    }

    function captureImage(video, modal) {
        const canvas = modal.querySelector("#cameraCanvas");
        const message = modal.querySelector("#cameraMessage");

        if (!video.videoWidth || !video.videoHeight) {
            message.textContent =
                "Camera is not ready yet. Please wait a moment.";
            return;
        }

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const context = canvas.getContext("2d");

        context.drawImage(
            video,
            0,
            0,
            canvas.width,
            canvas.height
        );

        const imageData = canvas.toDataURL("image/jpeg", 0.9);

        sessionStorage.setItem(
            "medtrust_camera_capture",
            imageData
        );

        message.textContent =
            "Image captured successfully.";

        setTimeout(() => {
            closeCamera();

            alert(
                "Image captured successfully. " +
                "Image-to-text extraction can be connected to the document analysis pipeline."
            );
        }, 500);
    }

    function closeCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }

        const modal =
            document.getElementById("medtrustCameraModal");

        if (modal) {
            modal.remove();
        }
    }

    cameraButton.addEventListener("click", openCamera);

    console.log("MEDTRUST AI camera.js loaded successfully.");
});