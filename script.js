  // Check if the browser supports camera access
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    // Prompt the user for camera access
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            // Display the video stream in a video element
            const videoElement = document.createElement('video');
            videoElement.srcObject = stream;
            videoElement.autoplay = true;
            document.body.appendChild(videoElement);
        })
        .catch((error) => {
            console.error('Error accessing the camera:', error);
        });
} else {
    console.error('Camera access is not supported in this browser.');
}
