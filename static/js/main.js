// UniNotes ERP - JavaScript général
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss des messages après 5 secondes
    document.querySelectorAll('.message-item').forEach(function(msg) {
        setTimeout(function() {
            msg.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(20px)';
            setTimeout(function() { msg.remove(); }, 400);
        }, 5000);
    });

    // Confirmation avant actions destructrices
    document.querySelectorAll('[data-confirm]').forEach(function(el) {
        el.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm || 'Confirmer cette action ?')) {
                e.preventDefault();
            }
        });
    });

    // Animations au scroll (IntersectionObserver)
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.card-hover, .stat-card').forEach(function(el) {
            observer.observe(el);
        });
    }
});
