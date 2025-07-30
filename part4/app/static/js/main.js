document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('form.delete-place-form').forEach(form => {
    form.addEventListener('submit', e => {
      if (!confirm('Are you sure you want to delete this place?')) {
        e.preventDefault();
      }
    });
  });
});

