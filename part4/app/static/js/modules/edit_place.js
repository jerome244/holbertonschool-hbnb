document.addEventListener('DOMContentLoaded', function () {
    const deleteButtons = document.querySelectorAll('.delete-photo-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const photoId = this.getAttribute('data-photo-id');
            const placeId = this.getAttribute('data-place-id');

            // Confirm with the user before deletion
            if (confirm('Are you sure you want to delete this photo?')) {
                fetch(`/place/${placeId}/photos/${photoId}/delete`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.error || 'An error occurred');
                        });
                    }
                    return response.json();  // Parse JSON if the response is ok
                })
                .then(data => {
                    // If photo was deleted successfully
                    alert(data.message || 'Photo deleted successfully!');
                    // Remove the photo from the UI dynamically
                    const photoItem = button.closest('.photo-item');
                    if (photoItem) {
                        photoItem.remove();  // Remove the photo item from the DOM
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert(error.message || 'Error deleting photo');
                });
            }
        });
    });
});
