document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('deployForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const image = document.getElementById('image').value;
        const command = document.getElementById('command').value;

        fetch('http://34.228.165.192:8000/deploy/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({image: image, command: command}),
        })
        .then(response => response.json())
        .then(data => {
            if(data && data.id) {
                document.getElementById("containerId").textContent = data.id;
                // Assuming there's a way to determine if the container is running from the response
                // Update the container status visually
                updateContainerStatus(data.id);
            } else {
                console.error('Container ID not received:', data);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    document.getElementById('executeForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const containerId = document.getElementById('containerId').textContent;
        const execCommand = document.getElementById('execCommand').value;

        fetch('http://34.228.165.192:8000/execute/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({container_id: containerId, command: execCommand}),
        })
        .then(response => response.json())
        .then(data => {
            const outputElement = document.getElementById('commandOutput');
            if(data.output) {
                outputElement.textContent = data.output.join('\n'); // Display the command output
            } else {
                outputElement.textContent = 'No output received.';
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

function updateContainerStatus(containerId) {
    // Example of how you might check and update the container's status
    // This function would need to be implemented based on how your backend provides status updates
    fetch(`http://34.228.165.192:8000/container_status/${containerId}`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        const statusIndicator = document.getElementById('containerIndicator');
        if (data.status === 'running') {
            statusIndicator.style.backgroundColor = 'green';
        } else if (data.status === 'exited' || data.status === 'stopped') {
            statusIndicator.style.backgroundColor = 'red';
        } else {
            statusIndicator.style.backgroundColor = 'grey';
        }
    })
    .catch(error => {
        console.error('Error fetching container status:', error);
        // Handle error, maybe update the UI to show an error status
    });
}
