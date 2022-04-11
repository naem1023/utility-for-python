"""
한글 자소 추출, 자소를 이용해서 유니코드 글자 완성
"""
from enum import IntEnum

def onset(char):
    code = ord(char)
    if 0xac00 <= code <= 0xd7b0:
        return (code - 0xac00) // 588
    return -1


def nucleus(char):
    code = ord(char)
    if 0xac00 <= code <= 0xd7b0:
        x = (code - 0xac00) % 588
        return x // 28
    return -1


def coda(char):
    code = ord(char)
    if 0xac00 <= code <= 0xd7b0:
        return (code - 0xac00) % 28
    return -1


def compose(on, nu, cd):
    # print('{:#x}'.format(0xac00 + on * 588 + nu * 28 + cd))
    return chr(0xac00 + on * 588 + nu * 28 + cd)


onsets = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]  # 19개

nuclei = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ",
          "ㅣ"]  # 21개
codas = ["@", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ",
         "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]  # 28개

# nuclei= {
#     0: ("ㅏ", "a"),
#     1: ("ㅐ", "ai"),
#     2: ("ㅑ", "ya"),
#     3: ("ㅒ", "yai"),
#     4: ("ㅓ", "eo"),
#     5: ("ㅔ", "eoi"),
#     6: ("ㅕ", "yeo"),
#     7: ("ㅖ", "yeoi"),
#     8: ("ㅗ", "o"),
#     9: ("ㅘ", "wa"),
#     10: ("ㅙ", "wai"),
#     11: ("ㅚ", "oi"),
#     12: ("ㅛ", "yo"),
#     13: ("ㅜ", "u"),
#     14: ("ㅝ", "weo"),
#     15: ("ㅞ", "weoi"),
#     16: ("ㅟ", "ui"),
#     17: ("ㅠ", "yu"),
#     18: ("ㅡ", "eu"),
#     19: ("ㅢ", "eui"),
#     20: ("ㅣ", "i")
# }  # 21개
#
# from enum import Enum
# class SemiNucleus:
#     I = 1,
#     Y = 2,
#     W = 3
#
# rev_nuclei = {}
# for k, v in nuclei.items():
#     rev_nuclei[v[1]] = k
#

nu_del_i_map = {
    5: 4,  # ㅔ, ㅓ
    1: 0,  # ㅐ, ㅏ
    16: 13,  # ㅟ, ㅜ
    11: 8,  # ㅚ, ㅗ
    3: 2,  # ㅒ, ㅑ
    7: 6,  # ㅖ,ㅕ
    # 10: 9,  # ㅙ, ㅘ
    # 15: 14,  # ㅞ, ㅝ
}


def nu_del_i(c):
    nu = nucleus(c)
    if nu in nu_del_i_map:
        return nu_del_i_map[nu]
    return -1


#
# def nu_add(c, syl: SemiNucleus):
#     nu = nucleus(c)
#     r, e = add_nuclei(nu, syl)
#     if r < 0:
#         raise NucleusError(e)
#     return r


class On(IntEnum):
    ㄱ = 0
    ㄲ = 1
    ㄴ = 2
    ㄷ = 3
    ㄸ = 4
    ㄹ = 5
    ㅁ = 6
    ㅂ = 7
    ㅃ = 8
    ㅅ = 9
    ㅆ = 10
    ㅇ = 11
    ㅈ = 12
    ㅉ = 13
    ㅊ = 14
    ㅋ = 15
    ㅌ = 16
    ㅍ = 17
    ㅎ = 18


class Nu(IntEnum):
    ㅏ = 0
    ㅐ = 1
    ㅑ = 2
    ㅒ = 3
    ㅓ = 4
    ㅔ = 5
    ㅕ = 6
    ㅖ = 7
    ㅗ = 8
    ㅘ = 9
    ㅙ = 10
    ㅚ = 11
    ㅛ = 12
    ㅜ = 13
    ㅝ = 14
    ㅞ = 15
    ㅟ = 16
    ㅠ = 17
    ㅡ = 18
    ㅢ = 19
    ㅣ = 20


class Cd(IntEnum):
    無 = 0
    ㄱ = 1
    ㄲ = 2
    ㄳ = 3
    ㄴ = 4
    ㄵ = 5
    ㄶ = 6
    ㄷ = 7
    ㄹ = 8
    ㄺ = 9
    ㄻ = 10
    ㄼ = 11
    ㄽ = 12
    ㄾ = 13
    ㄿ = 14
    ㅀ = 15
    ㅁ = 16
    ㅂ = 17
    ㅄ = 18
    ㅅ = 19
    ㅆ = 20
    ㅇ = 21
    ㅈ = 22
    ㅊ = 23
    ㅋ = 24
    ㅌ = 25
    ㅍ = 26
    ㅎ = 27
