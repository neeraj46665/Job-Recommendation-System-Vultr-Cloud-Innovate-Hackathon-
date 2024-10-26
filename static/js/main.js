const analysisResultsCache = {};

document.querySelectorAll('.toggle-description').forEach(button => {
    button.addEventListener('click', function () {
        const content = this.nextElementSibling;
        content.style.display = content.style.display === 'block' ? 'none' : 'block';
    });
});

document.querySelectorAll('.analyze-form').forEach(form => {
    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent the form from submitting normally
        const formData = new FormData(this);
        const jobDescription = formData.get('job_description');
        const resultContainer = this.nextElementSibling;
        const loader = this.querySelector('.loader');
        const hideButton = resultContainer.querySelector('.hide-button');

        // Check if result is already cached
        if (analysisResultsCache[jobDescription]) {
            resultContainer.style.display = 'block';
            resultContainer.querySelector('.result-text').innerText = analysisResultsCache[jobDescription];
            hideButton.style.display = 'inline-block'; // Show hide button
            return;
        }

        // Show loader
        loader.style.display = 'inline-block';

        // Clear any previous results
        resultContainer.style.display = 'none';
        resultContainer.querySelector('.result-text').innerText = '';

        fetch('/analyze', {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                // Hide loader
                loader.style.display = 'none';

                // Cache the result
                analysisResultsCache[jobDescription] = data.analysis_results;

                resultContainer.style.display = 'block';
                resultContainer.querySelector('.result-text').innerText = data.analysis_results;
                hideButton.style.display = 'inline-block'; // Show hide button
            })
            .catch(error => {
                console.error('Error:', error);
                // Hide loader even if there's an error
                loader.style.display = 'none';
            });
    });
});

document.querySelectorAll('.hide-button').forEach(button => {
    button.addEventListener('click', function () {
        const resultContainer = this.closest('.analysis-results');
        resultContainer.style.display = 'none';
        this.style.display = 'none';
    });
});

async function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    const responseDiv = document.getElementById("chat-log");

    // Append user message to chat log
    responseDiv.innerHTML += `<div>User: ${userInput}</div>`;

    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: userInput
        })
    });

    const data = await response.json();

    if (response.ok) {
        const botResponse = data.response;
        // Append bot response to chat log
        responseDiv.innerHTML += `<div>Bot: ${botResponse}</div>`;
    } else {
        // Handle errors
        responseDiv.innerHTML += `<div>Error: ${data.error}</div>`;
    }

    // Clear input field
    document.getElementById("user-input").value = '';
}

async function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    const responseDiv = document.getElementById("chat-log");

    // Append user message to chat log with the user-message class
    responseDiv.innerHTML += `<div class="user-message">User: ${userInput}</div>`;

    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: userInput
        })
    });

    const data = await response.json();

    if (response.ok) {
        const botResponse = data.response;
        // Append bot response to chat log with the bot-message class
        responseDiv.innerHTML += `<div class="bot-message">Bot: ${botResponse}</div>`;
    } else {
        // Handle errors
        responseDiv.innerHTML += `<div>Error: ${data.error}</div>`;
    }

    // Clear input field
    document.getElementById("user-input").value = '';

    // Scroll to the bottom of the chat log
    responseDiv.scrollTop = responseDiv.scrollHeight;
}