import logging


def get_webhook(repo, url):
    """Retrieve the GitHub webhook with the given url from the repo.

    Args:
        repo: the Repository to get the webhook for.
        url: the url of the webhook.

    Returns:
        Hook instance or None if the hook doesn't exist.
    """

    gh_repo = repo.owner.get().get_github_repo(repo.name)

    for hook in gh_repo.get_hooks():
        if hook.config.get('url') == url:
            return hook

    return None


def create_webhook(repo, url):
    """Create a GitHub webhook for the given Repository. This is intended to be
    idempotent, meaning it will check to see if the hook already exists before
    creating it.

    Args:
        repo: the Repository to create the webhook for.
        url: the webhook url.

    Returns:
        True if the webhook was successfully created or already exists, False
        if it failed to be created.
    """

    if get_webhook(repo, url):
        logging.debug('%s already has webhook %s' % (repo, url))
        return True

    gh_repo = repo.owner.get().get_github_repo(repo.name)

    hook = gh_repo.create_hook('web', {'url': url, 'content_type': 'json'},
                               events=['push'], active=True)

    return hook is not None


def delete_webhook(repo, url):
    """Delete the GitHub webhook for the given Repository.

    Args:
        repo: the Repository to delete the webhook for.
        url: the url of the webhook to delete.

    Returns:
        True if the hook was deleted, False if nothing was deleted.
    """

    hook = get_webhook(repo, url)

    if hook:
        logging.debug('Deleting webhook %s for %s' % (url, repo))
        hook.delete()
        return True

    return False

