(function () {
    'use strict';

    var MODES = {
        BASHCLI: 'sh',
        BASHSRV: 'sh',
        SELESRV: 'javascript'
    };

    function modeFor(select) {
        return MODES[select.value] || 'sh';
    }

    function setMode(widget, mode) {
        if (!widget || !widget.editor || typeof ace === 'undefined') {
            return false;
        }
        var session = widget.editor.getSession();
        var current = session.getMode();
        if (current && current.$id === 'ace/mode/' + mode) {
            widget.setAttribute('data-mode', mode);
            return true;
        }
        if (!ace.require('ace/mode/' + mode)) {
            return false;
        }
        var Mode = ace.require('ace/mode/' + mode).Mode;
        session.setMode(new Mode());
        widget.setAttribute('data-mode', mode);
        return true;
    }

    function widgetFor(select) {
        var container = select.closest('fieldset') || document;
        return container.querySelector('.django-ace-widget');
    }

    function syncSelect(select) {
        var widget = widgetFor(select);
        if (!setMode(widget, modeFor(select))) {
            window.setTimeout(function () {
                setMode(widget, modeFor(select));
            }, 0);
        }
    }

    function syncAll() {
        var selects = document.querySelectorAll('select[name="tipus"], select[name$="-tipus"]');
        for (var i = 0; i < selects.length; i++) {
            syncSelect(selects[i]);
        }
    }

    document.addEventListener('change', function (event) {
        var target = event.target;
        if (target && target.matches &&
                target.matches('select[name="tipus"], select[name$="-tipus"]')) {
            syncSelect(target);
        }
    });

    if (window.django && window.django.jQuery) {
        window.django.jQuery(document).on('formset:added', function () {
            window.setTimeout(syncAll, 0);
        });
    }

    if (document.readyState === 'complete') {
        window.setTimeout(syncAll, 0);
    } else {
        window.addEventListener('load', function () {
            window.setTimeout(syncAll, 0);
        });
    }
})();
