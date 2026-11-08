const newButton = document.getElementById('btn-new-tale'); // Button to start a new tale
const continueButton = document.getElementById('btn-continue'); // Button to continue an existing tale
const backButton = document.getElementById('btn-back'); // Button to go back to the title screen
const setupScreen = document.getElementById('screen-setup'); // The setup screen section
const titleScreen = document.getElementById('screen-title'); // The title screen section
const backgroundSelect = document.getElementById('background-select'); // The background selection dropdown
const customBackgroundField = document.getElementById('custom-background-field'); // The custom background input field
const setupForm = document.getElementById('setup-form'); // The setup form element
const gameScreen = document.getElementById('screen-game'); // The game screen section

// Event listener for the setup form submission
setupForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(setupForm)); // Convert form data to an object
    // Send the form data to the server to create a new campaign
    const response = await fetch('/api/campaigns', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    console.log(response.status);

    const result = await response.json();// Parse the JSON response from the server
    console.log(result.campaign_id);
});

// Event listener for the background selection dropdown
backgroundSelect.addEventListener('change', () => {
    if (backgroundSelect.value === 'custom') {
        customBackgroundField.hidden = false;
    } else {
        customBackgroundField.hidden = true;
    }
});


// Event listener for the "New Tale" button
newButton.addEventListener('click', () => {
    titleScreen.classList.remove('is-active');
    setupScreen.classList.add('is-active');
})

// Event listener for the "Back" button
backButton.addEventListener('click', () => {
    setupScreen.classList.remove('is-active');
    titleScreen.classList.add('is-active');
})