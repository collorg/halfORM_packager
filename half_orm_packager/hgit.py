"Provides the HGit class"

import os
import subprocess
from git import Repo

from half_orm_packager import utils

class HGit:
    "Manages the git operations on the repo."
    def __init__(self, base_dir=None):
        self.__base_dir = base_dir
        self.__repo: Repo = None
        if base_dir:
            self.__post_init()

    def __post_init(self):
        self.__repo = Repo(self.__base_dir)
        self.__current_branch = self.branch
        self.__is_clean = self.repos_is_clean()
        self.__last_commit = self.last_commit()

    def __str__(self):
        res = ['[Git]']
        res.append(f'- current branch: {self.__current_branch}')
        clean = utils.Color.green(self.__is_clean) if self.__is_clean else utils.Color.red(self.__is_clean)
        res.append(f'- repo is clean: {clean}')
        res.append(f'- last commit: {self.__last_commit}')
        return '\n'.join(res)

    def init(self, base_dir, release='0.0.0'):
        "Initiazes the git repo."
        cur_dir = os.path.abspath(os.path.curdir)
        self.__base_dir = base_dir
        subprocess.run(['git', 'init', base_dir], check=True)
        self.__repo = Repo(base_dir)
        os.chdir(base_dir)
        # Patch(self.__hop_cls, create_mode=True).patch(force=True, create=True)
        self.__repo.git.add('.')
        self.__repo.git.commit(m=f'[{release}] First release')
        self.__repo.git.checkout('-b', 'hop_main')
        self.__post_init()
        os.chdir(cur_dir)
        return self

    @property
    def branch(self):
        "Returns the active branch"
        return str(self.__repo.active_branch)

    @property
    def current_release(self):
        "Returns the current branch name without 'hop_'"
        return self.branch.replace('hop_', '')

    @property
    def is_hop_patch_branch(self):
        "Returns True if we are on a hop patch branch hop_X.Y.Z."
        try:
            major, minor, patch = self.current_release.split('.')
            return bool(1 + int(major) + int(minor) + int(patch))
        except ValueError:
            return False

    @staticmethod
    def repos_is_clean():
        "Returns True if the git repository is clean, False otherwise."
        with subprocess.Popen(
            "git status --porcelain", shell=True, stdout=subprocess.PIPE) as repo_is_clean:
            repo_is_clean = repo_is_clean.stdout.read().decode().strip().split('\n')
            repo_is_clean = [line for line in repo_is_clean if line != '']
            return not bool(repo_is_clean)

    def last_commit(self):
        """Returns the last commit
        """
        return list(self.__repo.iter_commits(self.branch, max_count=1))[0]

    def set_branch(self, release_s):
        """Checks the branch

        Either hop_main or hop_<release>.
        """
        rel_branch = f'hop_{release_s}'
        if str(self.branch) == 'hop_main' and rel_branch != 'hop_main':
            # creates the new branch
            self.__repo.create_head(rel_branch)
            self.__repo.git.checkout(rel_branch)
            print(f'NEW branch {rel_branch}')
        elif str(self.branch) == rel_branch:
            print(f'On branch {rel_branch}')
