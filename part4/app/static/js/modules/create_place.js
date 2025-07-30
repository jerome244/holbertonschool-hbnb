// create_place.js - Handles place creation for hosts

document.addEventListener('DOMContentLoaded', () => {
    const createPlaceForm = document.getElementById('create-place-form');

    createPlaceForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const title = document.getElementById('place-title').value;

        const description = document.getElementById('place-description').value;
        const price = document.getElementById('place-price').value;
        const location = document.getElementById('place-location').value;

        const response = await createPlace(name, description, price, location);

        if (response.ok) {
            alert('Place created successfully!');
            window.location.href = 'host_dashboard.html';
        } else {
            alert('Error creating place: ' + response.statusText);
        }
    });
});

// Function to send the place creation request
async function createPlace(name, description, price, location) {
    const token = getCookie('token');  // Get the JWT token for authentication
    const response = await fetch('https://your-backend-url/create-place', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`  // Add JWT token in the Authorization header
        },
        body: JSON.stringify({ name, description, price, location }),
    });
    return response;
}
