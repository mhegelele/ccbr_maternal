/**
 * Created by john on 08/06/16.
 */

var formEditor = function(formschema, formoptions) {
    var config = {};
    if ($.isEmptyObject(formschema)) {
        config.schema = {
            "title": "",
            "type": "object",
            "properties": {}
        };
    }
    else {
        config.schema = formschema;
    }

    if ($.isEmptyObject(formoptions)) {
        config.options = {
            "form": {
                "attributes": {
                    "action": "",
                    "method": "post"
                },
                "buttons": {
                    "submit": {}
                }
            },
            "fields": {}
        };
    }
    else {
        config.options = formoptions;
    }

    var setupEditor = function(id, json) {
        var text = "";
        if (json) {
            text = JSON.stringify(json, null, "    ");
        }

        var editor = ace.edit(id);
        editor.setTheme("ace/theme/textmate");
        editor.getSession().setMode("ace/mode/json");
        //editor.renderer.setHScrollBarAlwaysVisible(false);
        //editor.setShowPrintMargin(false);
        editor.setValue(text);

        setTimeout(function() {
            editor.clearSelection();
            editor.gotoLine(0,0);
        }, 100);

        return editor;
    };

    var editor1 = setupEditor('editor', config);
    var textEditor = $('input[name="text-editor"]');
    textEditor.val(editor1.getSession().getValue());

    var mainPreviewField = null;

    var doRefresh = function(el, buildInteractionLayers, disableErrorHandling, cb) {
        try {
            config = JSON.parse(editor1.getValue());
        }
        catch (e) {}

        if (config.schema) {
            config.options.focus = false;
            config.postRender = function(form) {
                if (buildInteractionLayers) {
                }

                cb(null, form);
            };
            config.error = function(err) {
                Alpaca.defaultErrorCallback(err);

                cb(err);
            };

            if (disableErrorHandling) {
                Alpaca.defaultErrorCallback = function(error) {
                    console.log("Alpaca encountered an error while previewing form -> " + error.message);
                };
            }
            else {
                Alpaca.defaultErrorCallback = Alpaca.DEFAULT_ERROR_CALLBACK;
            }

            $(el).alpaca(config);
        }
    };

    var refreshPreview = function(callback)
    {
        if (mainPreviewField)
        {
            mainPreviewField.getFieldEl().replaceWith("<div class='modal-body' id='previewDiv'></div>");
            mainPreviewField.destroy();
            mainPreviewField = null;
        }

        doRefresh($("#previewDiv"), false, false, function(err, form) {

            if (!err)
            {
                mainPreviewField = form;
            }

            if (callback)
            {
                callback();
            }

        });
    };

    // editor changes
    editor1.on('change', function() {
        textEditor.val(editor1.getSession().getValue());
        var btnSave = $('.btn-save');
        if (btnSave.html() == "Saved") {
            btnSave.html('Save');
            btnSave.removeClass('btn-default').addClass('btn-primary');
        }
    });

    // form preview
    $('.btn-preview').off().on('click', function() {
        setTimeout(function() {
            refreshPreview();
        }, 50);
    });
};