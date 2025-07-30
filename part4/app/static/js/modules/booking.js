// booking.js - Handles booking functionality

document.addEventListener('DOMContentLoaded', () => {
    const bookingForm = document.getElementById('booking-form');

    bookingForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const placeId = document.getElementById('place-id').value;
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        const response = await bookPlace(placeId, startDate, endDate);

        if (response.ok) {
            alert('Booking confirmed!');
            window.location.href = 'index.html';
        } else {
            alert('Error booking place: ' + response.statusText);
        }
    });
});

// Function to send booking request
async function bookPlace(placeId, startDate, endDate) {
    const token = getCookie('token');  // Get the JWT token for authentication
    const response = await fetch('https://your-backend-url/book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`  // Add JWT token in the Authorization header
        },
        body: JSON.stringify({ place_id: placeId, start_date: startDate, end_date: endDate }),
    });
    return response;
}
