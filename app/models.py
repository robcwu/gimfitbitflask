from app import db

def get_all_fitbit_credentials():
    return FitbitToken.query.all()

def get_user_fitbit_credentials(user_id):
    return FitbitToken.query.filter_by(user_id=user_id).first()


def save_fitbit_token(user_id, access_token, refresh_token):
    fitbit_info = get_user_fitbit_credentials(user_id)
    if not fitbit_info:
        fitbit_info = FitbitToken(None, None, None)
    fitbit_info.user_id = user_id
    fitbit_info.access_token = access_token
    fitbit_info.refresh_token = refresh_token
    db.session.add(fitbit_info)
    db.session.commit()
    return fitbit_info

class FitbitToken(db.Model):
    __tablename__ = 'fitbit_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), unique=True, index=True)
    refresh_token = db.Column(db.String(500))
    access_token = db.Column(db.String(500))

    def __init__(self, user_id, access_token, refresh_token):
        super(FitbitToken, self).__init__()
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __repr__(self):
        return '<Token {}, User {}>'.format(self.id, self.user_id)

    def __str__(self):
        return '{} {}'.format(self.id, self.user_id)
