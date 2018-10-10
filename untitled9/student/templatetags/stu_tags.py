
from django import template
from django.db.models import Sum

register = template.Library()

@register.simple_tag
def get_score(enroll_obj, customer_obj):
    study_record = enroll_obj.studyrecord_set.filter(course_record__from_class_id=enroll_obj.enrolled_class.id)

    for record in study_record:
        print('-->',record)

    return study_record.aggregate(Sum('score'))
