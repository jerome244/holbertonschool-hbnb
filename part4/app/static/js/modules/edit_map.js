document.addEventListener('DOMContentLoaded', function () {
    var mapDiv = document.getElementById('map');
    var latInput = document.getElementById('latitude');
    var lngInput = document.getElementById('longitude');
    var addrInput = document.getElementById('address-search');
    if (!mapDiv || !latInput || !lngInput || !addrInput) return;

    const initialLat = parseFloat(latInput.value) || 48.8566;
    const initialLng = parseFloat(lngInput.value) || 2.3522;

    var map = L.map('map').setView([initialLat, initialLng], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);

    var marker = L.marker([initialLat, initialLng], { draggable: true }).addTo(map);

    marker.on('dragend', function () {
        var latlng = marker.getLatLng();
        latInput.value = latlng.lat.toFixed(6);
        lngInput.value = latlng.lng.toFixed(6);
        // Reverse geocode to update address input
        fetchAddressFromLatLng(latlng.lat, latlng.lng);
    });

    map.on('click', function (e) {
        marker.setLatLng(e.latlng);
        latInput.value = e.latlng.lat.toFixed(6);
        lngInput.value = e.latlng.lng.toFixed(6);
        // Reverse geocode to update address input
        fetchAddressFromLatLng(e.latlng.lat, e.latlng.lng);
    });

    // Leaflet-Geosearch address search
    const provider = new window.GeoSearch.OpenStreetMapProvider();

    // Create suggestions container
    let suggestionsContainer = document.createElement('div');
    suggestionsContainer.style.position = 'absolute';
    suggestionsContainer.style.border = '1px solid #ccc';
    suggestionsContainer.style.background = 'white';
    suggestionsContainer.style.zIndex = '1000';
    suggestionsContainer.style.width = addrInput.offsetWidth + 'px';
    suggestionsContainer.style.maxHeight = '150px';
    suggestionsContainer.style.overflowY = 'auto';
    suggestionsContainer.style.display = 'none';
    addrInput.parentNode.appendChild(suggestionsContainer);

    // Position container just below input
    const rect = addrInput.getBoundingClientRect();
    suggestionsContainer.style.top = (addrInput.offsetTop + addrInput.offsetHeight) + 'px';
    suggestionsContainer.style.left = addrInput.offsetLeft + 'px';

    // Function to clear suggestions
    function clearSuggestions() {
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.style.display = 'none';
    }

    addrInput.addEventListener('input', async function () {
        const value = addrInput.value;
        if (value.length < 3) {
            clearSuggestions();
            return;
        }
        const results = await provider.search({ query: value });
        if (results.length) {
            clearSuggestions();
            results.forEach(result => {
                const item = document.createElement('div');
                item.textContent = result.label;
                item.style.padding = '5px';
                item.style.cursor = 'pointer';
                item.addEventListener('mousedown', function (e) {
                    e.preventDefault(); // prevent losing focus
                    addrInput.value = result.label;
                    marker.setLatLng([result.y, result.x]);
                    map.setView([result.y, result.x], 16);
                    latInput.value = result.y.toFixed(6);
                    lngInput.value = result.x.toFixed(6);
                    clearSuggestions();
                });
                suggestionsContainer.appendChild(item);
            });
            suggestionsContainer.style.display = 'block';
        } else {
            clearSuggestions();
        }
    });

    // Hide suggestions if click outside
    document.addEventListener('click', function (e) {
        if (!suggestionsContainer.contains(e.target) && e.target !== addrInput) {
            clearSuggestions();
        }
    });

    // ---- Reverse Geocode on page load ----
    function fetchAddressFromLatLng(lat, lng) {
        fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`, { credentials: "include" })
            .then(response => response.json())
            .then(data => {
                if (data.display_name) {
                    addrInput.value = data.display_name;
                }
            });
    }

    // On page load: set address for current lat/lng
    fetchAddressFromLatLng(initialLat, initialLng);
});
