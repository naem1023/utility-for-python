from git import Repo
import os
import argparse
import numpy as np
import sys
import platform

# 현재 파일의 repository root directory 찾기
def search_root_Git():
    git_repo = Repo('.', search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    repo = Repo(git_root)

    return repo

# os 별 경로 구분자 지정
def set_path_separator():
    os = platform.system()
    if os == 'Windows':
        return '\\'
    else:
        return '/'

class Scan:
    res_files = []
    # dt = ''
    test_mode = False
    
    all_flag = None
    staged_modified_files = None
    untracked_modified_files = None
    modified_files = None
    notstaged_tracked_modified_files = None

    path_separator = None

    def __init__(self,
                 test_mode=False,
                 all_flag=False):
        self.test_mode = test_mode
        self.path_separator = set_path_separator()

        # 현재 git repository를 체크하여 원하는 파일들만 train set으로 지정
        self.check_git_status(all_flag)
        
        self.collect_res_files(self.test_mode)
    
    def check_git_status(self, all_flag):
        self.all_flag = all_flag
    
        # option '-all'
        # git에서 수정된 파일 이름들을 가져온다
        if self.all_flag:
            self.notstaged_tracked_modified_files = self.check_notstaged_modified_files()
            self.staged_modified_files = self.check_staged_files()
            self.untracked_modified_files = self.check_untracked_files()
            
        # 수정된 파일들만 train set으로 지정
        if self.staged_modified_files is None and self.untracked_modified_files is None \
            and self.notstaged_tracked_modified_files is None:
            print("there's no modified files")
        else:
            self.modified_files = np.concatenate((self.staged_modified_files, self.untracked_modified_files, self.notstaged_tracked_modified_files))
        
    def check_notstaged_modified_files(self):
        repo = search_root_Git()

        # 하나의 str 결과를 얻는다
        one_string_modified_files = np.array([repo.git.diff(name_only=True)])

        # '\n'로 split
        split_by_enter = np.char.split(one_string_modified_files, sep='\n')
        
        
        split_by_enter = np.stack(split_by_enter.ravel()).astype(str)
        
        # 경로 구분자로 split
        split_by_slash = np.char.split(split_by_enter[0], sep=self.path_separator)

        target_files = np.array([])

        # 파일 이름만 추출
        for file_path in split_by_slash:
            target_files =  np.append(target_files, np.array(file_path[-1]))
                
        return target_files
        
    def check_staged_files(self):
        repo = search_root_Git()

        # 현재 repository에서 modified tracked files(staged files)를 가져온다
        staged_filesPath = np.array([diff.a_path for diff in repo.index.diff("HEAD")])

        # 경로 구분자를 기준으로 split
        split_staged_filesPath = np.char.split(staged_filesPath, sep=self.path_separator)
        
        
        target_files = np.array([])

        # 파일 이름만 가져온다
        for file_path in split_staged_filesPath:
            target_files =  np.append(target_files, np.array(file_path[-1]))

        return target_files

    def check_untracked_files(self):
        repo = search_root_Git()

        # 현재 repository에서 untracked files(unstaged files)를 가져온다
        untracked_filesPath = np.array(repo.untracked_files)

        # 경로 구분자를 기준으로 split
        split_untracked_filesPath = np.char.split(untracked_filesPath, sep=self.path_separator)

        target_files = np.array([])

        # 파일 이름만 가져온다
        for file_path in split_untracked_filesPath:
            target_files =  np.append(target_files, np.array(file_path[-1]))

        return target_files

    def print_files(self):
        print('res_files!!!', self.res_files)
        
    def scan_tree(self, p, ext):
        with os.scandir(p) as it:
            for entry in it:
                if entry.is_dir(follow_symlinks=False):
                    yield from self.scan_tree(entry.path, ext)
                elif entry.is_file() and entry.name.endswith(ext):
                    if self.modified_files is None:
                        yield entry
                    elif entry.name in self.modified_files:
                        yield entry    
                else:
                    continue

    def scan_sub_dirs(self, dirs, file_type, ext):
        base = os.path.join('.', '')

        for d in dirs:
            p = os.path.join(base, d)
            if not os.path.exists(p):
                continue
            res_files = []
            for entry  in self.scan_tree(p, ext):
                res_files.append((entry.path, file_type))
            res_files.sort()
            self.res_files.extend(res_files)

    def collect_res_files(self, test_mode=False):
        self.res_files = []
        self.scan_sub_dirs(['debugs/tei'], 'TEI', '.txt')
        self.scan_sub_dirs(['debugs/nwrw'], 'NWRW', '.txt')
        self.scan_sub_dirs(['addons'], 'YML', '.yaml')
        tei_dirs = ['spoken-teis']
        self.scan_sub_dirs(tei_dirs, "TEIS", '.txt')
        if not test_mode:
            nwrw_dirs = ['nwrw']
            self.scan_sub_dirs(nwrw_dirs, "NWRW", '.txt')
            # tei_dirs = ['written-teis', 'spoken-teis']
            tei_dirs = ['written-teis']
            self.scan_sub_dirs(tei_dirs, "TEI", '.txt')

parser = argparse.ArgumentParser()
parser.add_argument('-modified', dest="all", help="pre processing all modified train set", action='store_true')

parser.set_defaults(all=False)

args = parser.parse_args()
print("args", args)
print("args.all", args.all)

haha = Scan(False, args.all)

haha.print_files()