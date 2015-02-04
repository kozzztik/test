from django.test import TestCase
from django.test.client import Client
import json
from main import loaded_models, models_defs, SUPPORTED_FIELDS
        
INSERTS_COUNT = 10

class EditorTest(TestCase):
    "Test that all pages are opening"
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200, "Index pages opens")
        
    def test_details(self):
        for model in loaded_models.keys():
            response = self.client.get('/details/', {'model': model})
            self.assertEqual(response.status_code, 200, "Model %s page opens" % (model,))
    
    def check_data(self, data):
        for model_name in loaded_models.keys():
            model_data = data[model_name]
            model_def = models_defs[model_name]
            for rec in model_data:
                pk = rec['id']
                model = loaded_models[model_name]
                objs = model.objects.filter(pk=pk)
                self.assertEquals(objs.count(), 1, 
                                  "Object of model %s with id %s not found in DB" % (model_name, pk))
                obj = objs[0]
                for field_def in model_def['fields']:
                    field_id = field_def['id']
                    field_type = SUPPORTED_FIELDS[field_def['type']]
                    value1 = field_type.serialize(getattr(obj, field_id, None))
                    value2 = rec[field_id]
                    self.assertEquals(value1, value2, 
                                      "Field %s value of model %s with id %s value differs from expected" % 
                                      (field_id, model_name, pk))
            
    def test_editing(self):
        # for every model generate some inserts
        my_data = {}
        
        for model_name in loaded_models.keys():
            model_def = models_defs[model_name]
            my_data[model_name] = []
            for x in range(INSERTS_COUNT):
                params = {}
                rec = {}
                for field_def in model_def['fields']:
                    field_type = SUPPORTED_FIELDS[field_def['type']]
                    value = field_type.serialize(field_type.random_value())
                    field_id = field_def['id']
                    rec[field_id] = value
                    params[field_id] = value
                response = self.client.post(
                    '/details/', 
                    data = json.dumps({'model': model_name, 'data': params}), 
                    content_type = 'application/json')
                self.assertEqual(response.status_code, 200, "Model %s gets new item" % (model_name,))
                resp_data = json.loads(response.content)
                rec['id'] = resp_data['id']
                my_data[model_name] += [rec]
                
        self.check_data(my_data)
        # for every model generate update every field
        for model_name in loaded_models.keys():
            model_def = models_defs[model_name]
            model_data = my_data[model_name]
            for rec in model_data:
                pk = rec['id']
                for field_def in model_def['fields']:
                    field_type = SUPPORTED_FIELDS[field_def['type']]
                    field_id = field_def['id']
                    params = {'model': model_name}
                    params['field_id'] = field_id
                    params['id'] = pk
                    value = field_type.serialize(field_type.random_value())
                    rec[field_id] = value
                    params['value'] = value
                    response = self.client.post(
                        '/edit/', 
                        data = json.dumps(params), 
                        content_type = 'application/json')
                    self.assertEqual(response.status_code, 200, "Model %s gets update" % (model_name,))
        self.check_data(my_data)