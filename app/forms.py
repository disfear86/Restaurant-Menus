from wtforms import Form, StringField, PasswordField, validators


class LoginForm(Form):
    email = StringField('', [validators.Length(max=50)])
    password = PasswordField('Password', [
        validators.Length(min=6),
        validators.DataRequired()
      ])


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [
        validators.Length(min=6, max=64),
        validators.Email()
        ])
    password = PasswordField('Password', [
        validators.Length(min=6),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
      ])
    confirm = PasswordField('Repeat Password')


class NewRestaurant(Form):
    name = StringField('', [validators.Length(max=200)])


class EditRestaurant(Form):
    new_name = StringField('', [validators.Length(max=200)])


class NewMenuItem(Form):
    name = StringField("New dish name: ", [validators.Length(max=100)])
    description = StringField("New dish description: ", [validators.Length(max=300)])
    price = StringField("New dish price: ", [validators.Length(max=8)])
    course = StringField("New dish category: ", [validators.Length(max=250)])


class EditMenuItem(Form):
    new_name = StringField("New dish name: ", [validators.Length(max=100)])
    new_description = StringField("New dish description: ", [validators.Length(max=300)])
    new_price = StringField("New dish price: ", [validators.Length(max=8)])
    new_course = StringField("New dish category: ", [validators.Length(max=250)])
