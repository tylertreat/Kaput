import logging

from google.appengine.api import memcache

from github import Github
from github.AuthenticatedUser import AuthenticatedUser
from github.GithubException import GithubException
from github.Repository import Repository


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

    # TODO: this check is unneeded. GitHub returns an error if the hook exists.
    if get_webhook(repo, url):
        logging.debug('%s already has webhook %s' % (repo, url))
        return True

    gh_repo = repo.owner.get().get_github_repo(repo.name)

    try:
        hook = gh_repo.create_hook('web', {'url': url, 'content_type': 'json'},
                                   events=['push'], active=True)
    except GithubException, e:
        if e.status == 422:
            print '%s already has webhook %s' % (repo, url)
            return True
        else:
            raise

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


def get_user(user):
    """Retrieve the GitHub user object for the given User.

    Args:
        user: the User to retrieve the GitHub user for.

    Returns:
        GitHub AuthenticatedUser instance.
    """

    github = Github(user.github_token)
    gh_user = memcache.get('gh:user:%s' % user.key.id())

    if gh_user:
        return github.create_from_raw_data(AuthenticatedUser, gh_user)

    gh_user = github.get_user()
    memcache.set('gh:user:%s' % user.key.id(), gh_user.raw_data)

    return gh_user


def get_repos(user, repo_type='owner'):
    """Retrieve the User's GitHub repos.

    Args:
        user: the User to retrieve GitHub repos for.
        repo_type: the type of repos to fetch (all, owner, public, private,
                   member).

    Returns:
        list of Github Repository instances.
    """

    github = Github(user.github_token)
    repos = memcache.get('gh:repos:%s' % user.key.id())

    if repos:
        return [github.create_from_raw_data(Repository, r) for r in repos]

    gh_user = github.get_user()
    repos = gh_user.get_repos(type=repo_type)
    memcache.set('gh:repos:%s' % user.key.id(), [r.raw_data for r in repos])

    return repos

