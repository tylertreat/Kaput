from kaput.auth.decorators import admin_required
from kaput.cron.blueprint import blueprint


@admin_required
@blueprint.route('/sync')
def sync_users():
    """Asynchronously sync users with GitHub."""
    from kaput.auth.user import sync_users

    sync_users()

    return '', 202

