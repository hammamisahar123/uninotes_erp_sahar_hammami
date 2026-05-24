(function($) {
    'use strict';

    function toggleTuteurField($roleField) {
        var $tuteurRow = $roleField.closest('.form-row').siblings('.field-tuteur');
        if ($tuteurRow.length === 0) {
            $tuteurRow = $roleField.closest('.inline-related, fieldset').find('.field-tuteur');
        }
        if ($roleField.val() === 'etudiant') {
            $tuteurRow.show();
        } else {
            $tuteurRow.hide();
        }
    }

    function initTuteurToggle($context) {
        $context = $context || $(document);
        $context.find('select[id$="-role"], #id_role').each(function() {
            var $field = $(this);
            toggleTuteurField($field);
            $field.on('change', function() {
                toggleTuteurField($(this));
            });
        });
    }

    $(document).ready(function() {
        initTuteurToggle();
        $(document).on('formset:added', function(e, $row) {
            initTuteurToggle($row);
        });
    });

})(django.jQuery);
