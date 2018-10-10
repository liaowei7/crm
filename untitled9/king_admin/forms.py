

from django.forms import forms ,ModelForm
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from crm import models

# class CustomerModelForm(ModelForm):
#     class Meta:
#         model = models.Customer
#         fields = "__all__"


def create_model_form(request,admin_class):
    '''动态生成MODEL FORM'''

    def __new__(cls, *args, **kwargs):

        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            #field_obj.widget.attrs['maxlength'] = getattr(field_obj,'max_length') if hasattr(field_obj,'max_length') else ""
            if field_name in admin_class.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'

            if hasattr(admin_class,"clean_%s"%field_name):
                field_clean_func = getattr(admin_class,"clean_%s"%field_name)
                setattr(cls,"clean_%s"%field_name,field_clean_func)

        return ModelForm.__new__(cls)

    def default_clean(self):
        """gei suo you de form jia yi ge yan zhen"""
        #print("--------running default clean",self)
        error_list = []

        for field in admin_class.readonly_fields:
            field_val = getattr(self.instance,field) #val in db
            if hasattr(field_val,"selected_related"): #m2m
                m2m_objs = getattr(field_val,"selected_related")
                m2m_vals = [i[0] for i in m2m_objs.values_list('id')]
                set_m2m_vals = set(m2m_vals)
                set_m2m_vals_from_frontend = set([i.id for i in self.cleaned_data.get(field)])
                if set_m2m_vals != set_m2m_vals_from_frontend:
                    # error_list.append(ValidationError(
                    #     _("Field %(field)s is Readonly"),
                    #     code='invalid',
                    #     params={'field': field},
                    # ))
                    self.add_error(field,"readonly")
                continue
            field_val_from_frontend = self.cleaned_data.get(field)

            print("--------running default clean",field,field_val,field_val_from_frontend)

            if field_val != field_val_from_frontend:
                error_list.append( ValidationError(
                    _("Field %(field)s is Readonly value,data should be %(value)s"),
                                      code='invalid',
                                      params={'field':field,'value':field_val},
                                      ))

        #readonly_table check
        if admin_class.readonly_table:
            raise ValidationError(
                _("Table is readonly, cannot be modified or added"),
                code='invalid',
            )

        #invoke user's customized form validation
        self.ValidationError=ValidationError
        response = admin_class.default_form_validation(self)
        if response:
            error_list.append(response)

        if error_list :
            raise ValidationError(error_list)


    class Meta:
        model = admin_class.model
        fields = "__all__"
        exclude = admin_class.modelform_exclude_fields

    attrs = {"Meta":Meta,"__new__":__new__}
    _model_form_class = type("DynamicModelForm",(ModelForm,), attrs)

    setattr(_model_form_class,"clean",default_clean)

    return _model_form_class