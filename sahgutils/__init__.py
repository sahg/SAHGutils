try:
    from sahgutils.__dev_version import version as __version__
    from sahgutils.__dev_version import git_revision as __git_revision__
except ImportError:
    from sahgutils.__version import version as __version__
    from sahgutils.__version import git_revision as __git_revision__

