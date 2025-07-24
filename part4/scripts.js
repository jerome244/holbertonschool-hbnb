/*
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

document.addEventListener('DOMContentLoaded', () => {

    function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    placesList.innerHTML = ''; // Clear any previous content
    placesList.appendChild('ul')

    places.forEach(place => {
      const placeElement = document.createElement('li');
      placeElement.className = 'place_card';

      // Customize below based on the actual data structure
      placeElement.innerHTML = `
        <h3>${place.title}</h3>
      `;

      placesList.appendChild(placeElement);
    });
  }


  async function getPlaces() {
    const url = "https://localhost:5000/api/v1/places";
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const places = await response.json();
      console.log(places)
      displayPlaces(places)
    } catch (error) {
      console.error(error.message);
    }
}
  getPlaces(); // Call function when DOM is ready

  });
