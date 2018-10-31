from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField, DateTimeField, BooleanField, HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email, Optional
import datetime

from web import db


class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))


class Alias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
    alias = db.Column(db.String(255), index=True, nullable=False)
    forward = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.Text, default='')
    enabled = db.Column(db.Boolean, default=True)
    expires = db.Column(db.DateTime, default=None)

    num_accepted = db.Column(db.Integer, default=0)
    num_rejected = db.Column(db.Integer, default=0)

    domain = db.relationship('Domain', backref=db.backref('aliases', lazy=True))
    owner = db.relationship('User', backref=db.backref('aliases'))


class QueuedEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orig_send_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_retry_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    from_addr = db.Column(db.String(128), nullable=False)
    to_addr = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)


class SystemStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_incoming = db.Column(db.Integer, default=0)
    rejected_addresses = db.Column(db.Integer, default=0)


def get_system_stats():
    s = db.session.query(SystemStats).first()
    if s is None:
        s = SystemStats()
        db.session.add(s)
        db.session.commit()

    return s


class CreateAliasForm(Form):
    action = HiddenField('action', default='create')

    alias = StringField('Alias', [InputRequired()])
    domain = SelectField('Domain', coerce=int)
    forward = EmailField('Forward Address', [InputRequired(), Email()])
    comment = StringField('Comment', [Optional()])
    expires = DateTimeField('Expires', [Optional()])

    submit = SubmitField("Create Alias")


class UpdateAliasForm(Form):
    id = HiddenField('id', [InputRequired()])

    domain = HiddenField('Domain')
    alias = StringField('Alias', [InputRequired()])
    forward = EmailField('Forward Address', [InputRequired(), Email()])
    comment = StringField('Comment', [Optional()])
    expires = DateTimeField('Expires', [Optional()])

    enabled = BooleanField('Enabled', [Optional()])

    def populate(self, alias):
        self.id.data = alias.id
        self.alias.data = alias.alias
        self.domain.data = alias.domain.name
        self.forward.data = alias.forward
        self.comment.data = alias.comment
        self.enabled.data = alias.enabled
        self.expires.data = alias.expires
