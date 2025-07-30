// index.js - Fetches and displays the list of places

document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
});

// Function to check authentication (check if the JWT token exists)
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    
    if (!token) {
        loginLink.style.display = 'block';
    } else {
        loginLink.style.display = 'none';
        fetchPlaces(token);  // If authenticated, fetch places
    }
}

// Function to get the cookie value by its name
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return value;
    }
    return null;
}

// Function to fetch places and display them
async function fetchPlaces(token) {
    const response = await fetch('https://your-backend-url/places', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (response.ok) {
        const places = await response.json();
        displayPlaces(places);
    } else {
        alert('Failed to load places: ' + response.statusText);
    }
}

// Function to display places on the index page
function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    placesList.innerHTML = '';

    places.forEach(place => {
        const placeElement = document.createElement('div');
        placeElement.classList.add('place-card');
        placeElement.innerHTML = `
            <h3>${place.title}</h3>

            <p>${place.price_per_night}</p>
            <button class="details-button" onclick="viewPlaceDetails('${place.id}')">View Details</button>
        `;
        placesList.appendChild(placeElement);
    });
}

// Function to navigate to the details page for a specific place
function viewPlaceDetails(placeId) {
    window.location.href = `place.html?id=${placeId}`;
}
