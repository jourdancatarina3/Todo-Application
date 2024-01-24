from decimal import Decimal

from django.forms import ModelForm as DjangoModelForm
from django.forms import Form as DjangoForm


def field_to_dict(bound_field, initial=None):
    """ Returns a dict containing the properties of the given form field.

    Arguments:
        * bound_field - the django form's bound field. You can get this by
                form_instance[field_name]
        * initial - the desired initial value of the field
    """
    field = bound_field.field
    field_dict = {
        'name': bound_field.name,
        'help_text': bound_field.help_text,
        'label': bound_field.label,
        'value': initial or field.initial,
        'required': field.required,
        'auto_id': bound_field.auto_id,
        'html_name': bound_field.html_name
    }
    max_length = getattr(field, 'max_length', None)
    if max_length is not None:
        field_dict['max_length'] = max_length
    min_length = getattr(field, 'min_length', None)
    if min_length is not None:
        field_dict['min_length'] = min_length
    choices = getattr(field, 'choices', None)
    if choices is not None:
        field_dict['choices'] = list(choices)
    return field_dict


class Form(DjangoForm):

    def as_dict(self):
        """ Returns a dict containing the information from the form including
        the attributes of its fields.
        """
        form_dict = {
            'title': self.__class__.__name__,
            'prefix': self.prefix,
            'fields': {}
        }

        initial_data = {}

        for name in self.fields:
            initial = self.initial.get(name)
            if type(initial) == Decimal:
                initial = float(initial)
            field_dict = field_to_dict(
                bound_field=self[name], initial=initial)
            form_dict['fields'][name] = field_dict
            initial_data[name] = field_dict['value']

        form_dict['data'] = initial_data
        return form_dict


class ModelForm(Form, DjangoModelForm):
    pass
