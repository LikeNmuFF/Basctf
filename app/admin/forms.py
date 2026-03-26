from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from ..utils import CATEGORIES, DIFFICULTIES


class ChallengeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=CATEGORIES, validators=[DataRequired()])
    difficulty = SelectField('Difficulty', choices=DIFFICULTIES, validators=[DataRequired()], default='medium')
    points = IntegerField('Points', validators=[DataRequired(), NumberRange(min=1, max=10000)])
    link = StringField('Link (optional)', validators=[Optional(), Length(max=500)],
                       description='External link for the challenge (e.g., GitHub repo, documentation)')
    hint_1 = TextAreaField('Hint 1', validators=[Optional(), Length(max=1000)], description='Hint 1 (cost 25 points)')
    hint_2 = TextAreaField('Hint 2', validators=[Optional(), Length(max=1000)], description='Hint 2 (cost 50 points)')
    hint_3 = TextAreaField('Hint 3', validators=[Optional(), Length(max=1000)], description='Hint 3 (cost 100 points)')
    flag = StringField('Flag', validators=[DataRequired(), Length(max=256)],
                       description='Plain text flag — will be hashed before storage.')
    attachment = FileField('Attachment (optional)', validators=[
        Optional(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'zip', 'tar', 'gz', 'rar', '7z', 'exe', 'bin', 'pcap', 'sql', 'xml', 'json', 'py', 'js', 'html', 'css'], 'Allowed types only.')
    ])
    submit = SubmitField('Create Challenge')


class EditChallengeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=CATEGORIES, validators=[DataRequired()])
    difficulty = SelectField('Difficulty', choices=DIFFICULTIES, validators=[DataRequired()], default='medium')
    points = IntegerField('Points', validators=[DataRequired(), NumberRange(min=1, max=10000)])
    link = StringField('Link (optional)', validators=[Optional(), Length(max=500)],
                       description='External link for the challenge (e.g., GitHub repo, documentation)')
    hint_1 = TextAreaField('Hint 1', validators=[Optional(), Length(max=1000)], description='Hint 1 (cost 25 points)')
    hint_2 = TextAreaField('Hint 2', validators=[Optional(), Length(max=1000)], description='Hint 2 (cost 50 points)')
    hint_3 = TextAreaField('Hint 3', validators=[Optional(), Length(max=1000)], description='Hint 3 (cost 100 points)')
    flag = StringField('New Flag (leave blank to keep current)',
                       validators=[Optional(), Length(max=256)])
    attachment = FileField('Replace Attachment (optional)', validators=[
        Optional(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'zip', 'tar', 'gz', 'rar', '7z', 'exe', 'bin', 'pcap', 'sql', 'xml', 'json', 'py', 'js', 'html', 'css'], 'Allowed types only.')
    ])
    submit = SubmitField('Update Challenge')
