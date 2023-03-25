import datetime
from django import forms
from django.forms.widgets import DateInput
from django.forms import inlineformset_factory
from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    id = forms.CharField(required=True, max_length=10, label='Mã số')
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu')
    widget = {
        'password': forms.PasswordInput(),
    }
    # profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Điền vào trường này nếu muốn thay đổi mật khẩu"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError("Email này đã được đăng ký")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                admin_id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("Email này đã được đăng ký")

        return formEmail

    def clean_id(self, *args, **kwargs):
        formID = self.cleaned_data['id']
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(id=formID).exists():
                raise forms.ValidationError("Mã số đã tồn tại. Vui lòng thử lại")
        else:  # Update
            dbID = self.Meta.model.objects.get(
                admin_id=self.instance.pk).admin.id
            if dbID != formID:
                if CustomUser.objects.filter(id=formID).exists():
                    raise forms.ValidationError("Mã số đã tồn tại. Vui lòng thử lại")

        return formID

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'id']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StudentForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    def clean_dob(self):
        date = self.cleaned_data['dob']
        if date > datetime.date.today():
            raise forms.ValidationError("Ngày sinh không thể trong tương lai!")
        return date

    class Meta(CustomUserForm.Meta):
        model = Student
        labels = {
            "last_name": "Họ",
            "first_name": "Tên",
            "profile_pic": "Ảnh",
            "gender": "Giới tính",
            "dob": "Ngày sinh",
            "pob": "Nơi sinh",
            "grade": "Lớp",
            "number": "Số điện thoại",
            "email": "Email",
            "address": "Địa chỉ",
            "major": "Ngành"
        }
        fields = CustomUserForm.Meta.fields + \
            ['last_name', 'first_name', 'profile_pic', 'gender', 'dob', 'pob', 'grade', 'number', 'address', 'major']
        widgets = {
            'dob': DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    def clean_dob(self):
        date = self.cleaned_data['dob']
        if date > datetime.date.today():
            raise forms.ValidationError("Ngày sinh không thể trong tương lai!")
        return date

    class Meta(CustomUserForm.Meta):
        model = Staff
        labels = {
            "last_name": "Họ",
            "first_name": "Tên",
            "profile_pic": "Ảnh",
            "gender": "Giới tính",
            "dob": "Ngày sinh",
            "pob": "Nơi sinh",
            "level": "Trình độ",
            "number": "Số điện thoại",
            "email": "Email",
            "address": "Địa chỉ",
            "department": "Bộ môn",
            "major": "Ngành"
        }
        fields = CustomUserForm.Meta.fields + \
            ['last_name', 'first_name', 'profile_pic', 'gender', 'dob', 'pob', 'level', 'number', 'address', 'department','major']
        widgets = {
            'dob': DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }


class DepartmentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Department
        labels = {
            "id": "Mã bộ môn",
            "name": "Tên bộ môn"
        }
        fields = ['id', 'name']


class MajorForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(MajorForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Major
        labels = {
            "id": "Mã ngành",
            "name": "Tên ngành",
            "department": "Bộ môn"
        }
        fields = ['id', 'name', 'department']


class GradeForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(GradeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Grade
        labels = {
            "id": "Mã lớp",
            "name": "Tên lớp",
            "major": "Ngành",
            "course": "Khóa"
        }
        fields = ['id', 'name', 'major', 'course']


class SubjectForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        labels = {
            "id": "Mã học phần",
            "name": "Tên học phần",
            "credit": "Số tín chỉ",
            "type": "Loại học phần",
            "major": "Ngành",
            "session": "Học kỳ"
        }
        fields = ['id', 'name', 'credit', 'type', 'major', 'session']


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        labels = {
            "name": "Học kỳ",
            "year": "Năm học"
        }
        fields = '__all__'


class RoomForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Room
        labels = {
            "name": "Tên phòng/dãy",
            "dimension": "Sức chứa",
        }
        fields = '__all__'


class AssignForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(AssignForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Assign
        labels = {
            "subject": "Tên học phần",
            "group": "Nhóm",
            "room": "Phòng",
            "grade": "Lớp",
            "staff": "Cán bộ giảng dạy",
            "period": "Tiết",
            "day": "Thứ"
        }
        fields = '__all__'


# AssignTimeFormset = inlineformset_factory(Assign, AssignTime, form=AssignTimeForm,
#     extra=1, can_delete=True, can_delete_extra=True)

# AssignFormSet = inlineformset_factory(
#     Assign, AssignTime, form=AssignTimeForm,
#     extra=1, can_delete=True, can_delete_extra=True
# )


class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        labels = {
            "date": "Ngày",
            "message": "Nội dung"
        }
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        labels = {
            "feedback": "Nội dung"
        }
        fields = ['feedback']


class LeaveReportStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        labels = {
            "date": "Ngày",
            "message": "Nội dung"
        }
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'placeholder': 'Select a date',
                       'type': 'date'
                       }),
        }


class FeedbackStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        labels = {
            "feedback": "Nội dung"
        }
        fields = ['feedback']


class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)
        self.fields['email'].disabled = True
        self.fields['id'].disabled = True

    class Meta(CustomUserForm.Meta):
        model = Student
        labels = {
            "last_name": "Họ",
            "first_name": "Tên",
            "profile_pic": "Ảnh",
            "gender": "Giới tính",
            "dob": "Ngày sinh",
            "pob": "Nơi sinh",
            "grade": "Lớp",
            "number": "Số điện thoại",
            "email": "Email",
            "address": "Địa chỉ",
            "major": "Ngành"
        }
        fields = CustomUserForm.Meta.fields + \
            ['last_name', 'first_name', 'profile_pic', 'gender', 'dob', 'pob', 'grade', 'number', 'address', 'major']


class ChangePassword(FormSettings):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Điển vào trường này nếu muốn thay đổi mật khẩu'}), label=False)

    def __init__(self, *args, **kwargs):
        super(ChangePassword, self).__init__(*args, **kwargs)

    class Meta:
        model = Student
        fields = ['password']


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)
        self.fields['email'].disabled = True
        self.fields['id'].disabled = True

    class Meta(CustomUserForm.Meta):
        model = Staff
        labels = {
            "last_name": "Họ",
            "first_name": "Tên",
            "profile_pic": "Ảnh",
            "gender": "Giới tính",
            "dob": "Ngày sinh",
            "pob": "Nơi sinh",
            "level": "Trình độ",
            "number": "Số điện thoại",
            "email": "Email",
            "address": "Địa chỉ",
            "major": "Ngành",
            "department": "Bộ môn"
        }
        fields = CustomUserForm.Meta.fields + \
            ['last_name', 'first_name', 'profile_pic', 'gender', 'dob', 'pob', 'level', 'number', 'address', 'major', 'department']


class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Học kỳ", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        labels = {
            "subject": "Học phần",
            "student": "Sinh viên",
            "exam": "Điểm số"
        }
        fields = ['subject', 'session_year', 'student', 'exam']


class CsvForm(forms.ModelForm):
    class Meta:
        model = Csv
        labels = {
            "file_name": "Import"
        }
        fields = ('file_name',)
