from main import loaded_models
from django.contrib import admin

for model_name in loaded_models.keys():
    model = loaded_models[model_name]
    admin.site.register(model)