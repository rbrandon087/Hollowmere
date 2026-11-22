const newButton = document.getElementById('btn-new-tale'); // Button to start a new tale
const continueButton = document.getElementById('btn-continue'); // Button to continue an existing tale
const backButton = document.getElementById('btn-back'); // Button to go back to the title screen
const setupScreen = document.getElementById('screen-setup'); // The setup screen section
const titleScreen = document.getElementById('screen-title'); // The title screen section
const backgroundSelect = document.getElementById('background-select'); // The background selection dropdown
const customBackgroundField = document.getElementById('custom-background-field'); // The custom background input field
const setupForm = document.getElementById('setup-form'); // The setup form element
const gameScreen = document.getElementById('screen-game'); // The game screen section
let currentCampaignId = null;
const actionForm = document.getElementById('action-form'); // The action form element
const playerInput = document.getElementById('player-input'); // The player input field
const rollButton = document.getElementById('btn-roll'); // Button to roll the dice
const d20Face = document.getElementById('d20-result'); // The element that displays the result of the d20 roll
const rollHistory = document.getElementById('roll-history'); // The element that displays the roll history
const leaveButton = document.getElementById('btn-quit'); // Button to leave the game

// Event listener for the action form submission
actionForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const action = playerInput.value; // Get the player's action input
    if (action.trim() === '') {// Ignore empty input
        return;
    }
    rollButton.disabled = true; // Disable the roll button while the action is being processed
    playerInput.disabled = true; // Disable the player input while the action is being processed
    addEntry(action, 'player');
    playerInput.value = ''; // Clear the input field after submitting
    const response = await fetch(`/api/campaigns/${currentCampaignId}/turns`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
    });
    const result = await response.json();
    addEntry(result.narration, 'narrator');
    rollButton.disabled = false; // Re-enable the roll button after the action is processed
    playerInput.disabled = false; // Re-enable the player input after the action is processed

})
// The element that displays the story log
const storyLog = document.getElementById('story-log'); // The element that displays the story log
function addEntry(text,type) {
    const entry = document.createElement('article')
    entry.className = 'entry entry--' + type;
    entry.textContent = text;
    storyLog.appendChild(entry);
}
// Update the ability score and modifier for a given ability ID and score in the character sheet
  function updateAbilityScore(id, score) {
        document.getElementById(`score-${id}`).textContent = score;
        const mod = Math.floor((score - 10) / 2);
        if (mod >= 0) {
            document.getElementById(`mod-${id}`).textContent = '+' + mod;
        } else {
            document.getElementById(`mod-${id}`).textContent = mod;
        }
    }

// Load the character sheet data from the server and update the UI accordingly
async function loadCharacterSheet() {
    const response = await fetch(`/api/campaigns/${currentCampaignId}`);
    const character = await response.json();
    console.log(character);

    document.getElementById('sheet-name').textContent = character.character_name;
    document.getElementById('sheet-genre').textContent = character.genre;

    updateAbilityScore('str', character.strength);
    updateAbilityScore('dex', character.dexterity);
    updateAbilityScore('con', character.constitution);
    updateAbilityScore('int', character.intelligence);
    updateAbilityScore('wis', character.wisdom);
    updateAbilityScore('cha', character.charisma);

    const satchel = document.getElementById('satchel');
    satchel.innerHTML = ''; // Clear the satchel contents initially

    for (const item of character.items) {
        const li = document.createElement('li');
        li.textContent = item;
        satchel.appendChild(li);
    }
}

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
    currentCampaignId = result.campaign_id;

    setupScreen.classList.remove('is-active'); // Hide the setup screen
    gameScreen.classList.add('is-active'); // Show the game screen
    loadCharacterSheet();

    const startResponse = await fetch(`/api/campaigns/${currentCampaignId}/start`, {
        method: 'POST'
    });
    const startResult = await startResponse.json();
    addEntry(startResult.narration, 'narrator');
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
// Event listener for the "Roll" button
rollButton.addEventListener('click', async () => {
    rollButton.disabled = true; // Disable the roll button while the roll is being processed
    const reason = playerInput.value; // Get the reason for the roll from the player input field
    playerInput.value = ''; // Clear the player input field after getting the reason

    const response = await fetch(`/api/campaigns/${currentCampaignId}/roll`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason })
    });
    const result = await response.json();
    d20Face.textContent = result.roll_result; // Display the result of the d20 roll
    const li = document.createElement('li');
    li.textContent = `${reason || 'Roll'}: ${result.roll_result}`;
    if (result.roll_result === 20) {
        li.classList.add('is-crit');
    } else if (result.roll_result === 1) {
        li.classList.add('is-fumble');
    }
    rollHistory.prepend(li);
    addEntry(`Rolled a d20: ${result.roll_result}`, 'roll');
    addEntry(result.narration, 'narrator');
    rollButton.disabled = false; // Re-enable the roll button after the roll is processed
});

// Event listener for the "Leave" button
leaveButton.addEventListener('click', () => {
    gameScreen.classList.remove('is-active');
    titleScreen.classList.add('is-active');
    storyLog.innerHTML = '';
    currentCampaignId = null;
})