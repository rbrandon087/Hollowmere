const newButton = document.getElementById('btn-new-tale'); // Button to start a new tale
const continueButton = document.getElementById('btn-continue'); // Button to continue an existing tale
const backButton = document.getElementById('btn-back'); // Button to go back to the title screen
const setupScreen = document.getElementById('screen-setup'); // The setup screen section
const titleScreen = document.getElementById('screen-title'); // The title screen section


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