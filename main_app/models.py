from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser


subject_choice = (
    (0, '0'),
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
)

time_slots = (
    ('1 - 2', '1 - 2'),
    ('1 - 3', '1 - 3'),
    ('1 - 4', '1 - 4'),
    ('1 - 5', '1 - 5'),
    ('2 - 3', '2 - 3'),
    ('2 - 4', '2 - 4'),
    ('2 - 5', '2 - 5'),
    ('3 - 4', '3 - 4'),
    ('3 - 5', '3 - 5'),
    ('4 - 5', '4 - 5'),
    ('6 - 7', '6 - 7'),
    ('6 - 8', '6 - 8'),
)

DAYS_OF_WEEK = (
    ('Thứ Hai', 'Thứ Hai'),
    ('Thứ Ba', 'Thứ Ba'),
    ('Thứ Tư', 'Thứ Tư'),
    ('Thứ Năm', 'Thứ Năm'),
    ('Thứ Sáu', 'Thứ Sáu'),
    ('Thứ Bảy', 'Thứ Bảy'),
)

gender_choice = (
    ('Nam', 'Nam'),
    ('Nữ', 'Nữ')
)

level_choice = (
    ('Giáo sư', 'Giáo sư'),
    ('Phó giáo sư', 'Phó giáo sư'),
    ('Tiến sĩ', 'Tiến sĩ'),
    ('Thạc sĩ', 'Thạc sĩ'),
    ('Đại học', 'Đại học')
)


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    name = models.CharField(max_length=15)
    year = models.CharField(max_length=20)

    def __str__(self):
        return self.name + " (" + self.year + ")"


class Room(models.Model):
    name = models.CharField(max_length=20)
    dimension = models.IntegerField()

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "PDT"), (2, "GV"), (3, "SV"))
    id = models.CharField(primary_key='True', max_length=10)
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    fcm_token = models.TextField(default="")  # For firebase notifications

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)


class Department(models.Model):
    id = models.CharField(primary_key='True', max_length=50)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Major(models.Model):
    id = models.CharField(primary_key='True', max_length=50)
    name = models.CharField(max_length=120)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, null=True, blank=False)

    def __str__(self):
        return self.name


class Grade(models.Model):
    id = models.CharField(primary_key='True', max_length=50)
    name = models.CharField(max_length=120)
    course = models.IntegerField(max_length=5)
    major = models.ForeignKey(Major, on_delete=models.DO_NOTHING, null=True, blank=False)

    def __str__(self):
        return self.name


class Student(models.Model):
    admin = models.OneToOneField(CustomUser, primary_key='True', on_delete=models.CASCADE, blank=False)
    last_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='images/')
    gender = models.CharField(max_length=3, choices=gender_choice)
    dob = models.DateField(null=True)
    pob = models.CharField(max_length=200, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.DO_NOTHING, null=True, blank=False)
    number = models.CharField(max_length=15, null=True)
    address = models.TextField(null=True)
    major = models.ForeignKey(Major, on_delete=models.DO_NOTHING, null=True, blank=False)

    def __str__(self):
        return '%s: %s' % (self.admin_id, self.last_name + " " + self.first_name)


class Staff(models.Model):
    admin = models.OneToOneField(CustomUser, primary_key='True', on_delete=models.CASCADE, blank=False)
    last_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    profile_pic = models.ImageField(null=True, blank=True, upload_to="images/")
    gender = models.CharField(max_length=3, choices=gender_choice)
    dob = models.DateField(null=True)
    pob = models.CharField(max_length=200, null=True)
    level = models.CharField(max_length=30, choices=level_choice)
    number = models.CharField(max_length=15, null=True)
    address = models.TextField(null=True)
    major = models.ForeignKey(Major, on_delete=models.DO_NOTHING, null=True, blank=False)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, null=True, blank=False)

    def __str__(self):
        return '%s: %s' % (self.admin_id, self.last_name + " " + self.first_name)


class Subject(models.Model):
    id = models.CharField(primary_key='True', max_length=50)
    name = models.CharField(max_length=120)
    credit = models.IntegerField(max_length=2)
    type = models.IntegerField(choices=subject_choice, max_length=2, null=True)
    fee = models.CharField(max_length=50, null=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    # def save(self, *args, **kwargs):
    #     price = None
    #     if int(self.type) == 0:
    #         price = 0
    #     elif int(self.type) == 1:
    #         price = 280000
    #     elif int(self.type) == 2:
    #         price = 332000
    #     elif int(self.type) == 3:
    #         price = 616000
    #     elif int(self.type) == 4:
    #         price = 730000
    #     else:
    #         pass
    #     self.fee = price * self.credit
    #     super().save(*args, **kwargs)
    #
    def __str__(self):
        return '%s: %s' % (self.id, self.name)


class Assign(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    group = models.CharField(max_length=5)
    period = models.CharField(max_length=50, choices=time_slots, null=True)
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.subject.name

    # def __str__(self):
    #     grade = Grade.objects.get(id=self.grade_id)
    #     sbj = Subject.objects.get(id=self.subject_id)
    #     staff = Staff.objects.get(id=self.staff_id)
    #     return '%s : %s : %s' % (sbj.name, grade.name, staff.last_name + " " + staff.first_name)


class Attendance(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.DO_NOTHING, null=True)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam = models.FloatField(default=0)
    score_character = models.CharField(max_length=3, null=True)
    score_4 = models.FloatField(default=0)
    avg = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if float(self.exam) >= 9 and float(self.exam) <= 10:
            self.score_character = "A"
            self.score_4 = 4
        elif float(self.exam) >= 8 and float(self.exam) <= 8.9:
            self.score_character = "B+"
            self.score_4 = 3.5
        elif float(self.exam) >= 7 and float(self.exam) <= 7.9:
            self.score_character = "B"
            self.score_4 = 3
        elif float(self.exam) >= 6.5 and float(self.exam) <= 6.9:
            self.score_character = "C+"
            self.score_4 = 2.5
        elif float(self.exam) >= 5.5 and float(self.exam) <= 6.4:
            self.score_character = "C"
            self.score_4 = 2
        elif float(self.exam) >= 5 and float(self.exam) <= 5.4:
            self.score_character = "D+"
            self.score_4 = 1.5
        elif float(self.exam) >= 4 and float(self.exam) <= 4.9:
            self.score_character = "D"
            self.score_4 = 1
        elif float(self.exam) < 4:
            self.score_character = "F"
            self.score_4 = 0
        else:
            pass
        super().save(*args, **kwargs)


class Csv(models.Model):
    file_name = models.FileField(upload_to='csv/')
    uploaded = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=False)

    def __str__(self):
        return f"File: {self.id}"


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.staff.save()
    if instance.user_type == 3:
        instance.student.save()
