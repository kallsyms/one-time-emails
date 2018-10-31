from flask import request, render_template, Blueprint, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy.sql import func

from .models import *

mail = Blueprint('mail', __name__)


@mail.route('/', methods=['GET', 'POST'])
@login_required
def index():
    for a in current_user.aliases:
        if a.expires is not None and datetime.datetime.utcnow() > a.expires:
            a.enabled = False
    db.session.commit()

    create_form = CreateAliasForm()
    create_form.domain.choices = [(d.id, d.name) for d in Domain.query.all()]

    update_form = UpdateAliasForm()

    if request.form.get('action') == 'create' and create_form.validate_on_submit():
        a = Alias(
            owner_id=current_user.id,
            domain_id=create_form.domain.data,
            alias=create_form.alias.data,
            forward=create_form.forward.data,
            comment=create_form.comment.data,
            expires=create_form.expires.data,
        )
        db.session.add(a)
        db.session.commit()

        # Return redirect so that the form clears
        return redirect(url_for('mail.index'))

    elif request.form.get('action') == 'update' and update_form.validate_on_submit():
        a = Alias.query.filter_by(owner_id=current_user.id, id=update_form.id.data).first_or_404()
        a.alias = update_form.alias.data.rsplit('@', 1)[0]
        a.forward = update_form.forward.data
        a.enabled = update_form.enabled.data

        if update_form.comment.data is not None:
            a.comment = update_form.comment.data

        db.session.commit()

        return redirect(url_for('mail.index'))

    elif request.form.get('action') == 'delete' and 'id' in request.form:
        a = Alias.query.filter_by(owner_id=current_user.id, id=request.form['id']).first_or_404()
        db.session.delete(a)
        db.session.commit()

        return redirect(url_for('mail.index'))

    update_forms = [UpdateAliasForm() for _ in range(len(current_user.aliases))]
    for i, alias in enumerate(current_user.aliases):
        update_forms[i].populate(alias)

    return render_template('aliases.html', create_form=create_form, update_forms=update_forms)


@mail.route('/stats')
@login_required
def stats():
    stats_dict = {}
    system_stats = get_system_stats()
    stats_dict['incoming_emails'] = system_stats.num_incoming
    stats_dict['rejected_addrs'] = system_stats.rejected_addresses
    stats_dict['queued_emails'] = db.session.query(func.count(QueuedEmail.id)).scalar()
    stats_dict['accepted_addrs'] = db.session.query(func.sum(Alias.num_accepted)).scalar() or 0
    return render_template('stats.html', system_stats=stats_dict, aliases=current_user.aliases)
