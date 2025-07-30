document.addEventListener('DOMContentLoaded', function() {
  // Your function to accept a booking and update the notification count
  const acceptBookingBtns = document.querySelectorAll('.accept-booking-btn');
  acceptBookingBtns.forEach(btn => {
    btn.addEventListener('click', function(event) {
      const bookingId = this.dataset.bookingId;  // Assuming bookingId is passed as a data attribute
      
      // Make a POST request to approve the booking
      fetch(`/host/bookings/${bookingId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      .then(response => response.json())
      .then(data => {
        // After booking is accepted, refresh the notification count
        fetch('/user/notifications/unread_count')
          .then(response => response.json())
          .then(data => {
            document.getElementById('unread-count').textContent = data.unread_count;
          });
        
        // You can also update the booking UI to reflect the change
        alert(data.message);  // Show a success message
      })
      .catch(error => {
        console.error('Error:', error);
      });
    });
  });
});



  // Toggle the notification dropdown
  const notificationBell = document.getElementById('notification-bell');
  const notificationList = document.getElementById('notification-list');
  notificationBell.addEventListener('click', function() {
    notificationList.classList.toggle('show');
    if (notificationList.classList.contains('show')) {
      // Fetch notifications when the dropdown is shown
      fetch('/user/notifications')
        .then(response => response.json())
        .then(data => {
          const notificationItems = data.notifications.map(notification => `
            <div class="notification-item ${notification.status === 'unread' ? 'unread' : ''}">
              <p>${notification.message}</p>
              <small>${notification.timestamp}</small>
            </div>
          `).join('');
          document.getElementById('notification-items').innerHTML = notificationItems;
        });
    }
  });

  // Mark all notifications as read
  const markAllBtn = document.getElementById('mark-all-btn');
  if (markAllBtn) {
    markAllBtn.addEventListener('click', function() {
      fetch('/user/notifications/mark_all_as_read', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => response.json())
      .then(data => {
        // Update the notification count
        document.getElementById('unread-count').textContent = '0';
        alert(data.message);  // Show success message
      });
    });
  }

