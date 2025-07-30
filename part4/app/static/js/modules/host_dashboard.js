// host_dashboard.js - Host-specific page logic

document.addEventListener('DOMContentLoaded', () => {
    const token = getCookie('token');
    
    // If not authenticated or not a Host, redirect to the home page
    if (!token || !isHost(token)) {
        window.location.href = 'index.html';  // Redirect to home page if not Host
    }

    // Proceed to fetch and display Host-specific data
    fetchHostPlaces(token);
});

// Function to check if the user is a Host based on the JWT token
function isHost(token) {
    const decoded = decodeJwt(token);
    return decoded.role === 'host';
}

// Function to decode JWT token (you can use a library like jwt-decode)
function decodeJwt(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}
