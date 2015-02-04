from django.views.generic import TemplateView, View
from main import loaded_models, models_defs, SUPPORTED_FIELDS
import json
from django.http import Http404, HttpResponse

class HomeView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        models = loaded_models
        models = [(model_name, models[model_name], models[model_name]._meta.verbose_name) 
                  for model_name in models.keys()]
        kwargs['models'] = models
        return kwargs
    
class DetailsView(View):
    def get(self, request, *args, **kwargs):
        model_name = request.GET['model']
        if not model_name in loaded_models:
            raise Http404()
        model = loaded_models[model_name]
        model_def = models_defs[model_name]
        recs = model.objects.all()
        data = []
        for rec in recs:
            data_record = {'pk': rec.pk}
            for field in model_def['fields']:
                field_name = field['id']
                data_val = getattr(rec, field_name)
                field_type = SUPPORTED_FIELDS[field['type']]
                data_val = field_type.serialize(data_val)
                data_record[field_name] = unicode(data_val)
            data += [data_record]
        return HttpResponse(json.dumps({'defs': model_def, 'data': data}))
    
    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        model_name = body['model']
        data = body['data']
        if not model_name in loaded_models:
            raise Http404()
        model = loaded_models[model_name]
        model_def = models_defs[model_name]
        fields = {}
        for field in model_def['fields']:
            field_id = field['id']
            field_data = data[field_id]
            field_type = SUPPORTED_FIELDS[field['type']]
            field_data = field_type.deserialize(field_data)
            fields[field_id] = field_data
        obj = model(**fields)
        obj.save()
        return HttpResponse(json.dumps({'id': obj.id}))
    
class EditView(View):
    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        model_name = body['model']
        if not model_name in loaded_models:
            raise Http404()
        model = loaded_models[model_name]
        model_def = models_defs[model_name]
        obj = model.objects.get(pk=body['id'])
        field_id = body['field_id']
        value = body['value']
        field = None
        for f in model_def['fields']:
            if f['id'] == field_id:
                field = f
                break
        if not field:
            return
        
        field_type = SUPPORTED_FIELDS[field['type']]
        value = field_type.deserialize(value)
        setattr(obj, field_id, value)
        obj.save()
        return HttpResponse('{}')