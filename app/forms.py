from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, IntegerField, SubmitField, SelectField, BooleanField, DecimalField
from wtforms.validators import DataRequired, Email, Optional, NumberRange
from wtforms.fields import DateField, TimeField, FieldList, FormField
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('client', 'Client'), ('psychologist', 'Psychologist')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class AvailabilitySlotForm(FlaskForm):
    time = TimeField('Available Time', validators=[Optional()])

class AvailabilityForm(FlaskForm):
    date = DateField('Available Date', validators=[DataRequired()])
    slots = FieldList(FormField(AvailabilitySlotForm), min_entries=3)
    add_another = BooleanField('Add another availability after this?')
    submit = SubmitField('Add Availability')

class TaskForm(FlaskForm):
    description = TextAreaField('Task Description', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    score = IntegerField('Task Score (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Assign Task')

class CompleteTaskForm(FlaskForm):
    task_photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('✔️ Mark as Completed')

class NoteForm(FlaskForm):
    content = TextAreaField('Note Content', validators=[DataRequired()])
    submit = SubmitField('Save Note')

class PsyProfileForm(FlaskForm):
    specialization = StringField("Specialization", validators=[DataRequired()])
    bio = TextAreaField("Currículo / Bio", validators=[Optional()])
    pricing = DecimalField("Price per Consultation (R$)", validators=[DataRequired(), NumberRange(min=0)], places=2)
    experience_years = IntegerField("Years of Experience", validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField("💾 Save")

class CliProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    birth_date = DateField("Date of Birth", format="%Y-%m-%d", validators=[Optional()])
    bio = TextAreaField("Bio", validators=[Optional()])
    submit = SubmitField("💾 Save")