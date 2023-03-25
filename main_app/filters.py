import django_filters
from django_filters import CharFilter

from .models import *


class StudentFilter(django_filters.FilterSet):
    admin_id = CharFilter(label='Mã số sinh viên')

    def __init__(self, *args, **kwargs):
       super(StudentFilter, self).__init__(*args, **kwargs)
       self.filters['grade_id'].label="Lớp"
       self.filters['major_id'].label = "Ngành"

    class Meta:
        model = Student
        fields = ['major_id', 'grade_id']


class StaffFilter(django_filters.FilterSet):
    admin_id = CharFilter(label='Mã số cán bộ')

    def __init__(self, *args, **kwargs):
       super(StaffFilter, self).__init__(*args, **kwargs)
       self.filters['department_id'].label="Bộ môn"
       self.filters['major_id'].label = "Ngành"

    class Meta:
        model = Staff
        fields = ['major_id', 'department_id', 'admin_id']


class SubFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
       super(SubFilter, self).__init__(*args, **kwargs)
       self.filters['major_id'].label = "Ngành"

    class Meta:
        model = Subject
        fields = ['major_id']
