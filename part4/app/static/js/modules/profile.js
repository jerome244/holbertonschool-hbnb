// profile.js - Handles updating user profile data

document.addEventListener('DOMContentLoaded', () => {
    const profileForm = document.getElementById('profile-form');
    
    profileForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        const response = await updateProfile(email, password);

        if (response.ok) {
            alert('Profile updated successfully!');
        } else {
            alert('Error updating profile: ' + response.statusText);
        }
    });
});

// Function to send update request to backend
async function updateProfile(email, password) {
    const token = getCookie('token');  // Get the JWT token for authentication
    const response = await fetch('https://your-backend-url/update-profile', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`  // Add JWT token in the Authorization header
        },
        body: JSON.stringify({ email, password }),
    });
    return response;
}
