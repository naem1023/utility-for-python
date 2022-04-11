import os
from git import Repo


# 현재 파일의 repository root directory 찾기
def search_Git():
    git_repo = Repo('.', search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    repo = Repo(git_root)

    return repo
def unlock_gitconfig(root_dir):
    git_config = os.path.join(root_dir, '.git/config.lock')

    os.system('rm -rf ' + git_config)

# core.quotepath 옵션 설정
# 해당 옵션이 false일 경우 한글 파일명도 git status에 제대로 출력
# previous_option에 따라서  git config를 최초로 확인한 것인지 확인
def gitconfig_quotepath(repo, previous_option=None):
    origin_option = None

    # 최초로 git config core.quotepath를 확인
    if previous_option is None:
        # 기존 옵션 저장
        if repo.config_reader().get_value('core', 'quotepath'):
            print("core.quotepath is true")
            origin_option = True
        else:
            print("core.quotepath is false")
            origin_option = False
            return False

        os.system("git config core.quotepath false")
        return origin_option
    
    # 이미 한번 git config core.quotepath를 확인 후 파일들을 가져옴
    else:
        if previous_option:
            os.system("git config core.quotepath true")

repo = search_Git()

origin_option = gitconfig_quotepath(repo)
gitconfig_quotepath(repo, origin_option)

# print(proejct_root_dir)
# git_config = os.path.join(proejct_root_dir, '.git/config')

# utf8_encoding_config = """[i18n] 
#         commitEncoding = utf-8 
#         logOutputEncoding = utf-8
#     """
