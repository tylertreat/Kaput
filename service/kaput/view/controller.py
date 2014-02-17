from kaput.view.blueprint import blueprint


@blueprint.route('/')
def index():
    return 'Hello, World!', 200

