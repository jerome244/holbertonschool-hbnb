document.addEventListener('DOMContentLoaded', () => {
    const priceInput = document.getElementById('price');
    const form = document.querySelector('form');  // Get the form element

    // When the user enters a max price and the input changes
    priceInput.addEventListener('input', () => {
        // Get the max price from the input field
        const maxPrice = priceInput.value;
        
        // Update the URL with the new max price filter
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('price', maxPrice);  // Add or update the price parameter in the URL
        
        // Redirect to the updated URL with the new price filter
        window.location.href = currentUrl.toString();
    });

    // Optional: If you want to trigger the form submission automatically
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        
        // Get the max price from the input field
        const maxPrice = priceInput.value;
        
        // Update the URL with the new max price filter
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('price', maxPrice);  // Add or update the price parameter in the URL
        
        // Redirect to the updated URL (acting like a form submission)
        window.location.href = currentUrl.toString();
    });
});
