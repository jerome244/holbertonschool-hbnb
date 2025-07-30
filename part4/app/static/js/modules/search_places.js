document.addEventListener('DOMContentLoaded', () => {
  const locationInput = document.getElementById('location');
  const autocompleteResults = document.getElementById('autocomplete-results');
  const latInput = document.getElementById('latitude');
  const lonInput = document.getElementById('longitude');
  const mapContainer = document.getElementById('map');

  let map = L.map('map').setView([46.2276, 2.2137], 6); // Default center France
  let marker = null;
  let placesLayer = L.layerGroup(); // Layer group to persist markers

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

    // After updating the marker, fetch places around the new location
    fetchPlaces(lat, lon);
  }

  // Event listener for location input (to search and update results)
  locationInput.addEventListener('input', () => {
    const query = locationInput.value;
    if (query) {
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
                autocompleteResults.innerHTML = '';
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
      autocompleteResults.innerHTML = '';
    }
  });

  // Event listener for click on the map to update location
  map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    locationInput.value = '';  // Clear location input when map clicked
    autocompleteResults.innerHTML = '';  // Clear autocomplete results
    updateMarkerPosition(lat, lon);  // Update marker and hidden lat/lon fields
  });

  // Function to fetch places based on lat and lon
  async function fetchPlaces(lat, lon) {
    const radius = 5000;  // Radius in meters (5 km)
    const url = `/places/api?lat=${lat}&lon=${lon}&radius=${radius}`;
    
    try {
      console.log(`Fetching places for lat: ${lat}, lon: ${lon}`);  // Debugging line
      const response = await fetch(url);
      const places = await response.json();
      console.log("Fetched places:", places);  // Debugging line
      
      if (places.length > 0) {
        placesLayer.clearLayers();  // Clear old markers
        addPlacesMarkers(places); // Add markers around the clicked pin
      } else {
        alert('No places found for this location.');
      }
    } catch (err) {
      console.error('Error fetching places:', err);
      alert('There was an error fetching places.');
    }
  }

  // Function to add place markers to the map
  function addPlacesMarkers(places) {
    console.log("Adding markers to map...");
    places.forEach(place => {
      const placeMarker = L.marker([place.latitude, place.longitude])
        .bindPopup(`<a href="/places/${place.id}"><b>${place.title}</b></a><br>Price: $${place.price}`);

      // Add event listener to the marker (click event on the pin)
      placeMarker.on('click', () => {
        updateMarkerPosition(place.latitude, place.longitude); // Recenter map to clicked pin
        fetchPlaces(place.latitude, place.longitude); // Fetch places near the clicked marker
      });

      placesLayer.addLayer(placeMarker);
    });
    placesLayer.addTo(map);
  }

  // Initialize the map with default marker if coordinates are available
  const initialLat = parseFloat(latInput.value) || 46.2276;
  const initialLon = parseFloat(lonInput.value) || 2.2137;
  updateMarkerPosition(initialLat, initialLon);
});
