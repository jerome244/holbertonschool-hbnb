// login.js - Handles the login process for users

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();  // Prevent the default form submission
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Send the login request
            const response = await loginUser(email, password);
            const data = await handleApiResponse(response);

            if (data) {
                document.cookie = `token=${data.access_token}; path=/`;  // Store the JWT token in the cookies
                
                // Redirect based on user role
                if (data.role === 'host') {
                    window.location.href = 'host_dashboard.html';  // Redirect Hosts to their dashboard
                } else {
                    window.location.href = 'index.html';  // Redirect Users to the home page
                }
            }
        });
    }
});

// Function to handle the login API request
async function loginUser(email, password) {
    const response = await fetch('https://your-backend-url/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });
    return response;
}
