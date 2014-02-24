from kaput.repository import CommitHunk


def blame(repo, filename, line_number):
    """Determine who was last responsible for the provided piece of code.

    Args:
        repo: the repository to look at.
        filename: name of the file to check.
        line_number: line number of the file to look up.

    Returns:
        name, email, and, optionally, User instance for the person responsible.
    """

    query = CommitHunk.query(ancestor=repo.key)
    query = query.filter(CommitHunk.filename == filename)
    query = query.filter(CommitHunk.lines == line_number)
    query = query.order(-CommitHunk.timestamp)

    hunk = query.get()

    if not hunk:
        return None, None, None

    commit = hunk.key.parent().get()

    author_key = commit.author

    author = author_key.get() if author_key else None
    author_name = commit.author_name
    author_email = commit.author_email

    return author_name, author_email, author

