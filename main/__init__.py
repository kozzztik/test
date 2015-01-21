from workdir import PROJECTDIR
from django.db import models as dj_models
from django.core.exceptions import ImproperlyConfigured
from django.utils.six import add_metaclass
from django.utils.timezone import get_current_timezone
from main import models as main_models
import yaml
import sys
import datetime

class BaseSerializer():
    def serialize(self, data):
        return data
    def deserialize(self, data):
        return data

class DataSerializer(BaseSerializer):
    def serialize(self, data):
        return data.strftime("%d.%m.%Y")

    def deserialize(self, data):
        date = datetime.datetime.strptime(data, "%d.%m.%Y")
        return datetime.datetime(date.year, date.month, date.day, tzinfo=get_current_timezone())
    
SUPPORTED_FIELDS = {}
SUPPORTED_FIELDS['int'] = (dj_models.IntegerField, (), {})
SUPPORTED_FIELDS['char'] = (dj_models.CharField, (), {'max_length': 200})
SUPPORTED_FIELDS['date'] = (dj_models.DateField, (), {}, DataSerializer())

sys.modules['main.models'] = main_models

loaded_models = {}
models_defs = {}
    
def get_model(name, title, fields):
    attrs = {}
    default_field = None
    for field in fields:
        field_title = field['title'] if 'title' in field else None
        if not 'id' in field:
            raise ImproperlyConfigured('One of field definitions have no id field.')
        field_id = field['id']
        field_type = field['type'] if 'type' in field else 'char'
        if not field_type in SUPPORTED_FIELDS:
            raise ImproperlyConfigured('Field type %s not supported.' % (field_type,))
        if not default_field and field_type == 'char':
            default_field = field_id
        field_class = SUPPORTED_FIELDS[field_type]
        field_kwargs = (field_class[2] if len(field_class) > 2 else {}) or {}
        field_kwargs['verbose_name'] = field_title
        model_field = field_class[0](*field_class[1], **field_kwargs)
        if field_id in attrs:
            raise ImproperlyConfigured('Field %s already exists.' % (field_id,))
        attrs[field_id] = model_field
    attrs['__module__'] = 'main.models'
    if default_field:
        attrs['__unicode__'] = (lambda m: getattr(m, default_field))
    attrs['Meta'] = type('Meta', (object,), {'app_label': 'main', 'verbose_name': title})
    model = dj_models.base.ModelBase(name, (dj_models.Model,), attrs)
    loaded_models[name] = model
    return model
                
files_list = [PROJECTDIR + 'test_models.yaml']

for file_path in files_list:
    f = open(file_path, 'r')
    try:
        data = f.readlines()
        data = ''.join(data)
        data = yaml.load(data)
    finally:
        f.close()
    for model_name in data.keys():
        model_data = data[model_name]
        title = model_data['title']
        fields = model_data['fields']
        model = get_model(model_name, title, fields)
        models_defs[model_name] = model_data
        setattr(main_models, model_name, model)
