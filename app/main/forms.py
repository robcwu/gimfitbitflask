from wtforms import Form, StringField


class DeviceUserForm(Form):
    state = StringField('Email address associated with fitbit device')