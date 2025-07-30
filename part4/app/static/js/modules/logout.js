// logout.js - Clears the JWT token and redirects to login page
document.addEventListener('DOMContentLoaded', () => {
    // Clear the JWT token from cookies
    document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    
    // Redirect to login page
    window.location.href = 'login.html';
});
