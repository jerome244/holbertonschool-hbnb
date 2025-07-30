document.addEventListener('DOMContentLoaded', () => {
  const locationInput = document.getElementById('location');
  const autocompleteResults = document.getElementById('autocomplete-results');
  const latInput = document.getElementById('latitude');
  const lonInput = document.getElementById('longitude');
  const mapContainer = document.getElementById('map');

  // Ensure the required DOM elements exist
  if (!latInput || !lonInput || !mapContainer) {
    console.error('Required DOM elements are missing.');
    return;
  }

  // Initial coordinates, falling back to the provided Flask values
  const initialLat = parseFloat(latInput.value) || 46.2276; // Default to France if empty
  const initialLon = parseFloat(lonInput.value) || 2.2137; // Default to France if empty
  console.log('Initial Coordinates:', initialLat, initialLon); // Debugging step to ensure valid coordinates

  // Initialize the map with Leaflet
  let map = L.map(mapContainer).setView([initialLat, initialLon], 13); // Set initial map view
  let marker = L.marker([initialLat, initialLon]).addTo(map); // Initial marker

  // Set up the OpenStreetMap tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map);

  // Function to update the marker position and form inputs dynamically
  function updateMarkerPosition(lat, lon) {
    if (!marker) {
      marker = L.marker([lat, lon]).addTo(map);
    } else {
      marker.setLatLng([lat, lon]);
    }
    map.setView([lat, lon], 13); // Center map on new location
    latInput.value = lat; // Update latitude form input
    lonInput.value = lon; // Update longitude form input
  }

  // Event listener for location input (to search and update results)
  locationInput.addEventListener('input', () => {
    const query = locationInput.value.trim(); // Remove leading/trailing spaces
    if (query) {
      // Use Nominatim API (OpenStreetMap) to get suggested locations
      fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}&addressdetails=1&limit=5`)
        .then(response => response.json())
        .then(data => {
          console.log('Search results:', data); // Log the response data
          autocompleteResults.innerHTML = ''; // Clear previous results
          if (data.length > 0) {
            data.forEach(place => {
              const listItem = document.createElement('li');
              listItem.textContent = place.display_name;
              listItem.addEventListener('click', () => {
                locationInput.value = place.display_name; // Update input with selected place
                autocompleteResults.innerHTML = ''; // Clear autocomplete
                updateMarkerPosition(place.lat, place.lon); // Update map and marker position
              });
              autocompleteResults.appendChild(listItem); // Add to result list
            });
          } else {
            autocompleteResults.innerHTML = '<li>No results found</li>'; // If no results
          }
        })
        .catch(error => {
          console.error('Error fetching location data:', error);
          autocompleteResults.innerHTML = '<li>Error fetching results</li>';
        });
    } else {
      autocompleteResults.innerHTML = ''; // Clear results if no query
    }
  });

  // Event listener for click on the map to update location
  map.on('click', function (e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    locationInput.value = ''; // Clear location input when map clicked
    autocompleteResults.innerHTML = ''; // Clear autocomplete results
    updateMarkerPosition(lat, lon); // Update marker and form inputs
  });

  // Initialize the map with default marker if coordinates are available
  updateMarkerPosition(initialLat, initialLon);
});

// Modal for Viewing Larger Photo
function showPhotoModal(src) {
  const modal = document.getElementById('photo-modal');
  const modalImg = document.getElementById('modal-img');

  // Ensure the modal and image element exist
  if (!modal || !modalImg) {
    console.error('Modal or image element is missing.');
    return;
  }

  // Set the clicked image source in the modal
  modalImg.src = src;
  modal.setAttribute('aria-hidden', 'false');
  modal.style.display = 'flex';

  setTimeout(() => {
    modal.style.opacity = 1; // Smooth fade-in effect
  }, 10);
}

// Close Modal
function closePhotoModal() {
  const modal = document.getElementById('photo-modal');

  // Ensure the modal element exists
  if (!modal) {
    console.error('Modal element is missing.');
    return;
  }

  modal.style.opacity = 0;
  setTimeout(() => {
    modal.style.display = 'none';
  }, 300); // Duration of the fade effect (in ms)

  modal.setAttribute('aria-hidden', 'true');
}
