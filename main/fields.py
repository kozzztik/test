from django.utils.timezone import get_current_timezone
from django.db import models
import datetime
import random
import string

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
    
class BaseField():
    django_field = None
    django_field_kwargs = {}
    
    def get_django_field(self, file_def):
        return self.django_field
    
    def get_django_field_kwargs(self, file_def):
        return self.django_field_kwargs
    
    def serialize(self, data):
        return data

    def deserialize(self, data):
        return data
    
    def random_value(self):
        raise NotImplementedError('You must implement random generator for tests')
    
class IntField(BaseField):
    django_field = models.IntegerField
    
    def random_value(self):
        return random.randint(0, 1000)
    
class StrField(BaseField):
    django_field = models.CharField
    django_field_kwargs =  {'max_length': 200}
    
    def random_value(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(random.randint(1,200)))

class DateField(BaseField):
    django_field = models.DateField
    
    def random_value(self):
        day = random.choice(range(1,29))
        month = random.choice(range(1, 13))
        year = random.choice(range(1950, 2048))
        return datetime.datetime(year, month, day)

    def serialize(self, data):
        return data.strftime("%d.%m.%Y")

    def deserialize(self, data):
        date = datetime.datetime.strptime(data, "%d.%m.%Y")
        return datetime.datetime(date.year, date.month, date.day, tzinfo=get_current_timezone())

SUPPORTED_FIELDS = {}

SUPPORTED_FIELDS['int'] = IntField()
SUPPORTED_FIELDS['char'] = StrField()
SUPPORTED_FIELDS['date'] = DateField()
