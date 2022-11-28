"""Provides the HGit class
"""

import os
import subprocess
import sys

# from datetime import date
# from time import sleep
from git import Repo #, GitCommandError
from git.exc import InvalidGitRepositoryError

class HGit:
    "docstring"
    def __init__(self, base_dir):
        self.__repo = Repo(base_dir)

    def hop_main_branch(self):
        """Sets the reference to hop_main branch. Creates the branch if it doesn't exist.
        """
        if not HGit.__hop_main:
            HGit.__hop_main = 'hop_main' in [str(ref) for ref in self.__repo.references]
        if not  HGit.__hop_main:
            sys.stderr.write('WARN: creating hop_main branch.\n')
            HGit.__hop_main = True
            self.__repo.git.checkout('-b', 'hop_main')

    @property
    def repo(self):
        "Return the git repo object"
        if self.__repo is None:
            self.__repo = Repo(self.__hop_cls.project_path)
        return self.__repo

    @property
    def branch(self):
        "Returns the active branch"
        return str(self.repo.active_branch)

    def init(self):
        "Initiazes the git repo."
        #pylint: disable=import-outside-toplevel
        from .patch import Patch
        from .update import update_modules

        subprocess.run(['git', 'init', self.__hop_cls.project_path], check=True)
        self.__repo = Repo(self.__hop_cls.project_path)
        os.chdir(self.__hop_cls.project_path)
        Patch(self.__hop_cls, create_mode=True).patch(force=True, create=True)
        self.__hop_cls.model.reconnect()  # we get the new stuff from db metadata here
        self.__hop_cls.last_release_s = '0.0.0'
        update_modules(self.__hop_cls)
        self.repo.git.add('.')
        self.repo.git.commit(m='[{}] First release'.format(self.__hop_cls.last_release_s))
        self.hop_main_branch()
        print("Patch system initialized at release '{}'.".format(self.__hop_cls.last_release_s))
        return self

    @property
    def commit(self):
        """Returns the last commit
        """
        return list(self.__repo.iter_commits(self.branch, max_count=1))[0]

    @staticmethod
    def repos_is_clean():
        with subprocess.Popen(
            "git status --porcelain", shell=True, stdout=subprocess.PIPE) as repo_is_clean:
            repo_is_clean = repo_is_clean.stdout.read().decode().strip().split('\n')
            repo_is_clean = [line for line in repo_is_clean if line != '']
            return not(bool(repo_is_clean))

    @classmethod
    def exit_if_repo_is_not_clean(cls):
        "Exits if the repo has uncommited changes."
        if self.repo_is_clean:
            repo_is_clean_s = '\n'.join(repo_is_clean)
            print(f"WARNING! Repo is not clean:\n\n{repo_is_clean_s}")
            cont = input("\nApply [y/N]?")
            if cont.upper() != 'Y':
                print("Aborting")
                sys.exit(1)


    def set_branch(self, release_s):
        """Checks the branch

        Either hop_main or hop_<release>.
        """
        rel_branch = f'hop_{release_s}'
        if str(self.branch) == 'hop_main' and rel_branch != 'hop_main':
            # creates the new branch
            self.repo.create_head(rel_branch)
            self.repo.git.checkout(rel_branch)
            print(f'NEW branch {rel_branch}')
        elif str(self.branch) == rel_branch:
            print(f'On branch {rel_branch}')
        # else:
        #     sys.stderr.write(f'Current branch is {self.branch}\n')

    @property
    def get_patch_path(self):
        next_ = str(self.branch)
        if next_[0:4] != 'hop_':
            sys.stderr.write('Not on a hop branch!\n')
            sys.exit(1)
        next_ = next_[4:]
        if next_ == 'main':
            next_release = self.__hop_cls.get_next_release()
            if next_release is None:
                return
            next_ = next_release['release_s']
        major, minor, patch = [int(elt) for elt in next_.split('.')]
        return f'{major}/{minor}/{patch}'
