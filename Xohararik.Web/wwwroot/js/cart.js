// Update cart badge count on page load
document.addEventListener('DOMContentLoaded', function () {
    fetch('/Cart/Count')
        .then(res => res.json())
        .then(data => {
            const badge = document.getElementById('cart-badge');
            if (badge) {
                badge.textContent = data.count;
                badge.style.display = data.count > 0 ? 'inline' : 'none';
            }
        })
        .catch(() => {}); // silently fail if session not ready
});
