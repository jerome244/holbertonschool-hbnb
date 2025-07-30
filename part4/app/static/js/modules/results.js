// results.js - Displays search results

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const location = params.get('location');
    const price = params.get('price');

    // Fetch and display results based on search query
    fetchSearchResults(location, price);
});

// Function to fetch search results
async function fetchSearchResults(location, price) {
    const response = await fetch(`https://your-backend-url/results?location=${location}&price=${price}`, { method: 'GET',, credentials: "include" });

    if (response.ok) {
        const results = await response.json();
        displayResults(results);
    } else {
        alert('Error fetching search results: ' + response.statusText);
    }
}

// Function to display results on the page
function displayResults(places) {
    const resultsContainer = document.getElementById('results-list');
    resultsContainer.innerHTML = '';  // Clear any previous results

    places.forEach(place => {
        const placeElement = document.createElement('div');
        placeElement.classList.add('place-card');
        placeElement.innerHTML = `
            <h3>${place.title}</h3>

            <p>${place.price_per_night}</p>
            <button onclick="viewPlaceDetails(${place.id})">View Details</button>
        `;
        resultsContainer.appendChild(placeElement);
    });
}

function viewPlaceDetails(placeId) {
    window.location.href = `place.html?id=${placeId}`;
}
