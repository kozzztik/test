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
    
    def get_model_object(self, model_name, pk):
        model = loaded_models[model_name]
        objs = model.objects.filter(pk=pk)
        self.assertEquals(objs.count(), 1, 
            "Object of model %s with id %s not found in DB" % (model_name, pk))
        return objs[0]
    
    def check_obj_field_values(self, obj, model_def, values):
        for field_def in model_def['fields']:
            field_id = field_def['id']
            field_type = SUPPORTED_FIELDS[field_def['type']]
            field_value = field_type.serialize(getattr(obj, field_id, None))
            self.assertIn(field_id, values, "Data for field %s is not provided" % (field_id,))
            exp_value = values[field_id]
            self.assertEquals(str(exp_value), str(field_value), 
                "Field %s value differs from expected" %  (field_id,))
        
    def check_data(self, data):
        for model_name in loaded_models.keys():
            model_data = data[model_name]
            model_def = models_defs[model_name]
            for rec in model_data:
                pk = rec['id']
                obj = self.get_model_object(model_name, pk)
                self.check_obj_field_values(obj, model_def, rec)
            
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
        
        # check data display
        for model_name in loaded_models.keys():
            response = self.client.get('/details/', {'model': model_name})
            self.assertEqual(response.status_code, 200, "Model %s page opens" % (model_name,))
            resp_data = json.loads(response.content)
            model_def = models_defs[model_name]
            data = resp_data['data']
            self.assertEqual(len(data), INSERTS_COUNT, "Model %s records count fits data" % (model_name,))
            for rec in data:
                pk = rec['pk']
                obj = self.get_model_object(model_name, pk)
                self.check_obj_field_values(obj, model_def, rec)
