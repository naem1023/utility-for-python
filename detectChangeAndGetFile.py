from git import Repo
import os

def check():
    # bare_repo = Repo.init(os.path.join('.', 'bare-repo'), bare=True)
    repo = Repo('.')
    # assert bare_repo

    # assert not bare_repo.is_dirty()

    # print(repo.untracked_files)

    changedFiles = [ item.a_path for item in repo.index.diff(None) ]

    print(changedFiles)

check()