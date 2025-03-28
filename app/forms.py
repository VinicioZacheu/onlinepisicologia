from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, IntegerField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, NumberRange
from wtforms.fields import DateField, TimeField, FieldList, FormField

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
    submit = SubmitField('✔️ Mark as Completed')

class NoteForm(FlaskForm):
    content = TextAreaField('Note Content', validators=[DataRequired()])
    submit = SubmitField('Save Note')