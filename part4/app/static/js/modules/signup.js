// signup.js - Handles the sign-up process for users

document.addEventListener('DOMContentLoaded', () => {
    if (checkAuthentication()) {
        window.location.href = 'index.html';  // Redirect to index if already authenticated
        return;
    }

    const signUpForm = document.getElementById('sign-up-form');
    
    if (signUpForm) {
        signUpForm.addEventListener('submit', async (event) => {
            event.preventDefault();  // Prevent form default submission
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const role = document.querySelector('input[name="role"]:checked').value;

            // Send the sign-up request
            const response = await signUpUser(email, password, role);
            const data = await handleApiResponse(response);

            if (data) {
                alert("User created successfully! You can now log in.");
                
                // Redirect based on role
                if (data.role === 'host') {
                    window.location.href = 'host_dashboard.html';  // Redirect Hosts to their dashboard
                } else {
                    window.location.href = 'index.html';  // Redirect Users to the home page
                }
            }
        });
    }
});

// Function to handle the sign-up API request
async function signUpUser(email, password, role) {
    const response = await fetch('https://your-backend-url/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, role }),
    });
    return response;
}
