var field_types = {};

function default_value(elem) {
    elem = elem.children();
    return elem.val();
}

function default_onclose(parent, event) {
    if (event) {
       elem = parent.children('input');
       elem.blur(event);
    }
}

field_types['char'] = {
    validator: function(field, data) {
         if (data.length == 0) { return "Обязательное значение"};
    },
    editor: function(parent, field, data, onclose) {
        parent[0].innerHTML = "<input name='" + field.id + "' value='" + data + "'></input>";
        default_onclose(parent, onclose);
    },
    get_data: default_value,
}
field_types['int'] = {
    validator: function(field, data) {
         if (isNaN(parseInt(data))) { 
            return "В этом поле могут быть только цифры";
         };
    },
    editor: function(parent, field, data, onclose) {
        parent[0].innerHTML =  "<input type='number' name='" + field.id + "'  value='" + data + "'></input>";
        default_onclose(parent, onclose);
    },
    get_data: default_value,

}
field_types['date'] = {
    validator: function(field, data) {
        var pattern = /(\d{2})\.(\d{2})\.(\d{4})/;
        var dt = new Date(data.replace(pattern,'$3-$2-$1'));
        if (isNaN(dt.getTime())) { return "Укажите дату в формате ДД.ММ.ГГГГ"}
    },
    editor: function(parent, field, data, onclose) {
        parent[0].innerHTML = "<input  class='date-selector' name='" + field.id + "' value='" + data + "'></input>";    
        parent.children("input").datepicker(datepicker_regional);
        if (onclose) {
            parent.children("input").datepicker("option", "onClose", onclose);
        }

    },
    get_data: default_value,

}