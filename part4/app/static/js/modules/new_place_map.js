document.addEventListener('DOMContentLoaded', () => {
  const locationInput = document.getElementById('location');
  const autocompleteResults = document.getElementById('autocomplete-results');
  const latInput = document.getElementById('latitude');
  const lonInput = document.getElementById('longitude');
  const mapContainer = document.getElementById('map');

  let map = L.map('map').setView([46.2276, 2.2137], 6); // Center France
  let marker = null;

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
    map.setView([lat, lon], 13);
    latInput.value = lat;
    lonInput.value = lon;
  }

  // Event listener for location input (to search and update results)
  locationInput.addEventListener('input', () => {
    const query = locationInput.value;
    if (query) {
      // Call a geocoding API (like Nominatim or Google Maps API) to get places
      // Example: Use Nominatim for OpenStreetMap (replace with actual API request)
      fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}&addressdetails=1&limit=5`)
        .then(response => response.json())
        .then(data => {
          autocompleteResults.innerHTML = '';
          if (data.length > 0) {
            data.forEach(place => {
              const listItem = document.createElement('li');
              listItem.textContent = place.display_name;
              listItem.addEventListener('click', () => {
                locationInput.value = place.display_name;
                autocompleteResults.innerHTML = ''; // Clear results
                updateMarkerPosition(place.lat, place.lon);
              });
              autocompleteResults.appendChild(listItem);
            });
          } else {
            autocompleteResults.innerHTML = '<li>No results found</li>';
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
  map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    locationInput.value = ''; // Clear location input when map clicked
    autocompleteResults.innerHTML = ''; // Clear autocomplete results
    updateMarkerPosition(lat, lon);
  });

  // Initialize the map with default marker if coordinates are available
  const initialLat = parseFloat(latInput.value) || 46.2276;
  const initialLon = parseFloat(lonInput.value) || 2.2137;
  updateMarkerPosition(initialLat, initialLon);
});
