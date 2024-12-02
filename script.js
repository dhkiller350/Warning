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

 async function fetchIPDetails() {
      try {
        const response = await fetch('https://ipapi.co/json/');
        const data = await response.json();
        document.getElementById('ip-address').textContent = data.ip;
        document.getElementById('location').textContent = `${data.city}, ${data.region}, ${data.country_name}`;
        document.getElementById('isp').textContent = data.org;
      } catch (error) {
        document.getElementById('ip-address').textContent = 'Error fetching data';
        document.getElementById('location').textContent = 'Error fetching data';
        document.getElementById('isp').textContent = 'Error fetching data';
      }
    }

    function playFBIAlert() {
      document.getElementById('fbiSound').play();
    }
}
