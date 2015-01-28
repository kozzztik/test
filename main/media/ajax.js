var current_model = '';

var csrftoken = $.cookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
});

var editor = '';
var editor_parent = '';
var editor_field = '';
var editor_row_id = '';
var myfocus = false;

function leave_js(row_id, field_id) {
    return "javascript: on_cell_click(" + row_id + ", '" + field_id + "');"
}

function on_editor_leave() {
    if (myfocus) { return;}
    var field_type=field_types[editor_field.type];
    var data = field_type.get_data(editor_parent);
    var error_text = field_type.validator(editor_field, data);
    var error_box = $('#error_box');
    var context_parent = editor_parent[0];
    
    if (error_text) {
        error_box[0].innerHTML = error_text;
        error_box.show();
        editor.focus();
    } else {
        error_box.hide();
        editor_parent[0].innerHTML = "<div class='loader'>";
        editor = '';
        editor_parent.attr('onclick', leave_js(editor_row_id, editor_field.id));
        $.ajax({
            dataType: "json",
            type : "POST",
            processData: false,
            url: '/edit/',
            data: JSON.stringify(
                { model: current_model, id: editor_row_id, 
                    field_id: editor_field['id'], value: data}
                ),
            success: function() {
                context_parent.innerHTML = data;
            },
            error: function() {
                error_box[0].innerHTML = 'Произошла неизвестная ошибка';
                error_box.show();
            },
        });
    }
}

function on_cell_click(row_id, field_id) {
    if (editor) { 
        on_editor_leave();
        return;
    }
    editor_parent = $('tr[row_id="' + row_id + '"] > td[field="' + field_id + '"]');
    var field_id = editor_parent.attr('field');
    editor_row_id = editor_parent.parent().attr('row_id');
    var data = editor_parent[0].innerHTML;
    model_def.fields.forEach(function(foo) {
        if (foo.id == field_id) { editor_field = foo; }
    });
    field_types[editor_field.type].editor(editor_parent, editor_field, data, on_editor_leave);
    editor_parent.removeAttr('onclick');
    editor = editor_parent.children('input[name="' + editor_field.id + '"]');
    myfocus = true;
    editor.focus();
    myfocus = false;
}

function load_model(model) {
    $.ajax({
        mode: "abort",
        port: "load_model",
        dataType: "json",
        type : "GET",
        url: '/details/',
        data: { model: model },
        success: function(data, textStatus, jqXHR ) {
            var html = "<h4>" + data.defs.title + '</h4>\n';
            html += '<div class="alert alert-error" id="error_box" style="display: none;"></div>';
            html += '<table class="table table-striped table-bordered"><thead><tr>';
            html += '<th>#</th>\n'
            data.defs.fields.forEach(function(field) {
                html += '<th>' + field.title + '</th>\n';
            });
            html += "</tr></thead>\n<tbody>\n";
            data.data.forEach(function(record) {
                html += '<tr row_id="' + record.pk + '">\n<td>' + record.pk + '</td>\n';
                data.defs.fields.forEach(function(field) {
                    html += '<td onclick="' + leave_js(record.pk, field.id) + '" field="' + field.id + '">'
                    html += record[field.id] + '</td>\n';
                });
                html += '</tr>\n';
            });
            html += "</table>\n";
            html += "<h4>Новый элемент</h4>\n";
            html += "<form class=form-horizontal id='add_form'>\n";
            data.defs.fields.forEach(function(field) {
                html += "<fieldset class='control-group' id='add_" + field.id +"'>\n";
                html += "<div class='control-label'><label>";
                html += field.title + ':</label></div>';
                html += "<div class='controls'><span class='editor'></span>";
                html += "<div class='help-inline' style='display: none;'></div>";
                html += "</div>"
                html += "</fieldset>";
            });            
            html += "<fieldset><div class='form-actions'>";
            html += '<button type="button" onclick="javascript: add_elem();" class="btn btn-primary">';
            html += "Добавить</button>";
            html += '<button class="submit btn" type="reset">Очистить</button>';
            html += "</div></fieldset>";
            html += "</form>";
            $('#content')[0].innerHTML = html;
            
            $('td.editable').click(on_cell_click);
            
            data.defs.fields.forEach(function(field) {
                var selector = $('#add_'+ field.id);
                field_types[field.type].editor($('#add_'+ field.id + ' .editor'), field, '');
            });
            
            current_model = model;
            model_def = data.defs;
            model_data = data.data;
        },
    });
}

function add_elem() {
    var add_data = {};
    var data_valid = true;
    model_def.fields.forEach(function(field) {
        var field_type = field_types[field.type];
        var fieldset =  $('#add_'+ field.id );
        var elem = $('#add_'+ field.id + ' .controls .editor');
        var helper = $('#add_'+ field.id + ' .controls .help-inline');
        var data = field_type.get_data(elem);
        var error_text = field_type.validator(field, data);
        if (error_text) {
            data_valid = false;
            fieldset.addClass("error");
            helper[0].innerHTML = error_text;
            helper.show();
        } else {
            fieldset.removeClass("error");
            helper.hide();
            add_data[field.id] = data;
        }
    });
    if (!data_valid) {return;}
    $.ajax({
        mode: "abort",
        port: "load_model",
        dataType: "text",
        processData: false,
        type : "POST",
        url: '/details/',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({ model: current_model, data: add_data }),
        success: function(data, textStatus, jqXHR ) {
            load_model(current_model);
        },
        error: function() {
            var error_box = $('#error_box');
            error_box[0].innerHTML = 'Произошла неизвестная ошибка';
            error_box.show();
        },
    });
}