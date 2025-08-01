document.addEventListener('DOMContentLoaded', function () {
  const notificationBell = document.getElementById('notification-bell');
  const notificationList = document.getElementById('notification-list');
  const notificationItems = document.getElementById('notification-items');
  const unreadCountEl = document.getElementById('unread-count');
  const markAllBtn = document.getElementById('mark-all-btn');

  // ✅ Load unread count on page load
  if (unreadCountEl) {
    fetch('/api/v1/notifications/unread_count')
      .then(res => res.json())
      .then(data => {
        unreadCountEl.textContent = data.unread_count || '0';
      })
      .catch(err => console.error('Unread count error:', err));
  }

  // ✅ Toggle dropdown and fetch notifications
  if (notificationBell && notificationList && notificationItems) {
    notificationBell.addEventListener('click', function () {
      notificationList.classList.toggle('show');

      if (notificationList.classList.contains('show')) {
        fetch('/api/v1/notifications/')
          .then(res => res.json())
          .then(data => {
            const html = data.notifications.map(n => `
              <div class="notification-item ${n.status === 'unread' ? 'unread' : ''}">
                <p>${n.message}</p>
                <small>${n.timestamp}</small>
              </div>
            `).join('');
            notificationItems.innerHTML = html || '<p>No notifications.</p>';
          })
          .catch(err => {
            console.error('Notification fetch error:', err);
            notificationItems.innerHTML = '<p>Failed to load notifications.</p>';
          });
      }
    });
  }

  // ✅ Mark all as read
  if (markAllBtn) {
    markAllBtn.addEventListener('click', function () {
      fetch('/api/v1/notifications/mark_all_as_read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
        .then(res => res.json())
        .then(data => {
          if (unreadCountEl) unreadCountEl.textContent = '0';
          alert(data.message || 'Marked all as read.');
        })
        .catch(err => {
          console.error('Error marking all as read:', err);
        });
    });
  }

  // ✅ Optional: Refresh count after accepting booking
  const acceptBookingBtns = document.querySelectorAll('.accept-booking-btn');
  acceptBookingBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const bookingId = this.dataset.bookingId;
      fetch(`/host/bookings/${bookingId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
        .then(res => res.json())
        .then(data => {
          // Refresh unread count
          if (unreadCountEl) {
            fetch('/api/v1/notifications/unread_count')
              .then(r => r.json())
              .then(data => {
                unreadCountEl.textContent = data.unread_count;
              });
          }
          alert(data.message);
        })
        .catch(err => {
          console.error('Booking approval error:', err);
        });
    });
  });
});
