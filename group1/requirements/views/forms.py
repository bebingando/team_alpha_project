from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User
from django.forms.extras.widgets import SelectDateWidget, Select
from django.forms.models import inlineformset_factory
from django.forms.widgets import ClearableFileInput

from requirements.models import user_association
from requirements.models.iteration import Iteration
from requirements.models.project import Project
from requirements.models.story import Story
from requirements.models.story_attachment import StoryAttachment
from requirements.models.story_comment import StoryComment
from requirements.models.task import Task
from django.forms.models import inlineformset_factory
from requirements.models.filemaker import PDF
import datetime


class SignUpForm(UserCreationForm):
    ROLES = (
        ('cli', 'Client'),
        ('own', 'Owner'),
        ('dev', 'Developer')
    )
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLES, required=True)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += 'form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'role',
            'username',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.is_active = False
        if commit:
            user.save()
        return user


class ChangePwdForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordChangeForm, self).__init__(self.user, *args, **kwargs)
        for name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += 'form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})


class UserProfileForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += 'form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password')


class IterationForm(forms.ModelForm):

    def __init__(self, *args, ** kwargs):
        super(IterationForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

    #   add by Zhi and Nora, to constraint the Iteration begin time
    def clean_start_date(self):
        self.startdate = self.cleaned_data['start_date']
        curdate = datetime.datetime.date(datetime.datetime.now())
        if curdate > self.startdate:
            raise forms.ValidationError(
                'Iteration begin date should be later than the current time!'
            )
        return self.startdate

    def clean_end_date(self):
        enddate = self.cleaned_data['end_date']
        if enddate < self.startdate:
            raise forms.ValidationError(
                'Iteration end date should be later than it\'s start date !')
        return enddate

    class Meta:
        model = Iteration
        fields = ('title', 'description', 'start_date', 'end_date',)
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.TextInput(attrs={'readonly': 'readonly'}),
            'end_date': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Project
        fields = ('title', 'description',)
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class SelectAccessLevelForm(forms.Form):
    # Dropdown list to select from one of the current access levels for a project.
    user_role = forms.ChoiceField(
        choices=(
            (user_association.ROLE_CLIENT, "Client"),
            (user_association.ROLE_DEVELOPER, "Developer"),
            (user_association.ROLE_OWNER, "Owner"),
        ),
        widget=Select(attrs={'class': 'form-control'})
    )


class StoryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # retrieve the parameter project, then call the superclass init
        self.project = kwargs.pop('project', None)
        super(StoryForm, self).__init__(*args, **kwargs)
        # change the origin field 'owner' to ChoiceField
        self.fields['owner'] = forms.ModelChoiceField(
            queryset=self.project.users.all(),
            empty_label='None',
            required=False
        )
        # add 'form-control' into all element's class attrtribute
        for name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean_hours(self):
        data = self.cleaned_data['hours']
        if data <= 0:
            raise forms.ValidationError('Hours should be greater than 0 !')
        return data

    class Meta:
        model = Story
        fields = (
            'title',
            'description',
            'reason',
            'test',
            'hours',
            'owner',
            'type',
            'status',
            'points',
            'priority',
            'pause'
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'reason': forms.Textarea(attrs={'rows': 5}),
            'test': forms.Textarea(attrs={'rows': 5}),
        }


class FileForm(forms.Form):
    file = forms.FileField(
        widget=ClearableFileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )


# class RegistrationForm(forms.Form):
# 	firstName = forms.CharField(label='First Name:', max_length=100)
# 	lastName = forms.CharField(label='Last Name:', max_length=100)
# 	emailAddress=forms.CharField(label='Email Address:', max_length=100)
# 	username=forms.CharField(label='Username:', max_length=100)
# 	password=forms.CharField(label='password:', max_length=100, widget=forms.PasswordInput())
# 	confirmPassword=forms.CharField(label='Confirm password:', max_length=100)


class CommentForm(forms.ModelForm):

    def __init__(self, *args, ** kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = StoryComment
        fields = ('title', 'comment',)
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }


class TaskForm(forms.ModelForm):

    def __init__(self, *args, ** kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Task
        fields = ('description',)
        widgets = {
            'description': forms.Textarea(attrs={'rows': 1}),
        }

TaskFormSet = inlineformset_factory(
    Story,
    Task,
    fields=(
        'description',
    ),
    form=TaskForm,
    extra=0)


class AttachmentForm(FileForm):

    def __init__(self, *args, ** kwargs):
        super(AttachmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StoryAttachment
        fields = ('name',)
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
        }


class PDFForm(forms.ModelForm):
    def __init__(self, *args, ** kwargs):
        super(PDFForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = PDF
        fields = (
            'iteration_description',
            'iteration_duration',
            'story_description',
            'story_reason',
            'story_test',
            'story_task',
            'story_owner',
            'story_hours',
            'story_status',
            'story_points',
            'pie_chart',
        )
