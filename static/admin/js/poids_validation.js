(function($) {
    'use strict';

    function updatePoidsTotal($formset) {
        var total = 0;
        $formset.find('input[id$="-poids"]').each(function() {
            var val = parseFloat($(this).val()) || 0;
            var $row = $(this).closest('.form-row, .inline-related');
            if ($row.length && !$row.hasClass('empty-form') && !$row.find('input[id$="-DELETE"]').is(':checked')) {
                total += val;
            }
        });
        return total;
    }

    function showPoidsIndicator($formset) {
        var $indicator = $formset.find('.poids-indicator');
        if ($indicator.length === 0) {
            $indicator = $('<div class="poids-indicator" style="padding:8px 12px;margin:8px 0;border-radius:6px;font-size:13px;font-weight:600;"></div>');
            $formset.find('h2').first().after($indicator);
        }
        var total = updatePoidsTotal($formset);
        if (total === 100) {
            $indicator.css({background: 'rgba(16,185,129,0.1)', color: '#065f46', border: '1px solid rgba(16,185,129,0.3)'});
            $indicator.html('<span style="margin-right:6px;">✓</span> Poids total : ' + total + '% (OK)');
        } else if (total > 0) {
            $indicator.css({background: 'rgba(239,68,68,0.08)', color: '#991b1b', border: '1px solid rgba(239,68,68,0.2)'});
            $indicator.html('<span style="margin-right:6px;">✗</span> Poids total : ' + total + '% (doit être 100%)');
        } else {
            $indicator.css({background: 'rgba(100,116,139,0.08)', color: '#475569', border: '1px solid rgba(100,116,139,0.2)'});
            $indicator.html('Aucune catégorie — ajoutez des catégories avec des poids totalisant 100%.');
        }
    }

    $(document).ready(function() {
        var $formset = $('.inline-group');
        if ($formset.length) {
            showPoidsIndicator($formset);
            $formset.on('change', 'input[id$="-poids"], input[id$="-DELETE"]', function() {
                showPoidsIndicator($formset);
            });
            $(document).on('formset:added formset:removed', function() {
                showPoidsIndicator($formset);
            });
        }
    });

})(django.jQuery);
