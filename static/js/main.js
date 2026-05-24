// UniNotes ERP - JavaScript général

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss des messages Django après 5 secondes
    document.querySelectorAll('.bg-emerald-50, .bg-red-50, .bg-amber-50, .bg-blue-50').forEach(function(msg) {
        if (msg.querySelector('[role="alert"]') || msg.innerText.trim()) {
            setTimeout(function() {
                msg.style.transition = 'opacity 0.3s ease';
                msg.style.opacity = '0';
                setTimeout(function() { msg.remove(); }, 300);
            }, 5000);
        }
    });
});
