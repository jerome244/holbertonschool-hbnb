// review.js - Handles the functionality of submitting reviews for places

document.addEventListener('DOMContentLoaded', () => {
    const reviewForm = document.getElementById('review-form');
    
    if (reviewForm) {
        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const reviewText = document.getElementById('review-text').value;
            const placeId = getPlaceIdFromURL();
            const token = getCookie('token');
            
            if (token) {
                const response = await submitReview(token, placeId, reviewText);
                if (response.ok) {
                    alert('Review submitted successfully!');
                    window.location.href = `place.html?id=${placeId}`;
                } else {
                    alert('Failed to submit review: ' + response.statusText);
                }
            } else {
                alert('You need to be logged in to submit a review.');
                window.location.href = 'login.html';
            }
        });
    }
});

// Function to submit a review
async function submitReview(token, placeId, reviewText) {
    const response = await fetch(`https://your-backend-url/places/${placeId}/reviews`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ review_text: reviewText }),
    });
    return response;
}
