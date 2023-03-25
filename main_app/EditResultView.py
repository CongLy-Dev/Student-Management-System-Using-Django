from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from .models import Subject, Staff, Student, StudentResult, Assign
from .forms import EditResultForm
from django.urls import reverse


class EditResultView(View):
    def get(self, request, *args, **kwargs):
        resultForm = EditResultForm()
        staff = get_object_or_404(Staff, admin_id=request.user)
        subjects = Assign.objects.filter(staff_id=staff)
        resultForm.fields['subject'].queryset = Subject.objects.filter(assign__in=subjects)
        context = {
            'form': resultForm,
            'page_title': "Cập nhật điểm"
        }
        return render(request, "staff_template/edit_student_result.html", context)

    def post(self, request, *args, **kwargs):
        form = EditResultForm(request.POST)
        context = {'form': form, 'page_title': "Cập nhật điểm"}
        if form.is_valid():
            try:
                student = form.cleaned_data.get('student')
                subject = form.cleaned_data.get('subject')
                exam = form.cleaned_data.get('exam')
                # Validating
                result = StudentResult.objects.get(student=student, subject=subject)
                result.exam = exam
                result.save()
                messages.success(request, "Cập nhật thành công")
                return redirect(reverse('edit_student_result'))
            except Exception as e:
                messages.warning(request, "Không thể cập nhật")
        else:
            messages.warning(request, "Không thể cập nhật")
        return render(request, "staff_template/edit_student_result.html", context)
