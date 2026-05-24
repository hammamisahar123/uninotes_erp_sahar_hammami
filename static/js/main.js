// UniNotes ERP - JavaScript général

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss messages après 5 secondes
    document.querySelectorAll('[role="alert"], .message').forEach(function(msg) {
        setTimeout(function() {
            msg.style.transition = 'opacity 0.3s ease';
            msg.style.opacity = '0';
            setTimeout(function() { msg.remove(); }, 300);
        }, 5000);
    });

    // Confirmation avant actions destructrices
    document.querySelectorAll('[data-confirm]').forEach(function(el) {
        el.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm || 'Confirmer ?')) {
                e.preventDefault();
            }
        });
    });
});
