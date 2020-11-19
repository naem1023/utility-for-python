#-*- coding: utf8 -*-
import argparse
import re
import jaso

import time
from multiprocessing import Process, Lock, Queue, Pool
import multiprocessing
import parmap

import operator
import numpy as np
from itertools import product

class AngleBracketError(Exception):
    def __str__(self):
        return "홑화살괄호의 형식이 올바르지 않습니다."

class CommaError(Exception):
    def __str__(self):
        return "쉼표의 사용 방식이 올바르지 않습니다."

class NotHangeulError(Exception):
    def __str__(self):
        return "한글 이외의 문자는 허용되지 않습니다."

class DuplicateHangeulError(Exception):
    def __str__(self):
        return "중복된 자모는 허용되지 않습니다."

class NotCorrectLocationHangeulError(Exception):
    def __str__(self):
        return "자모가 한글 정규식의 올바른 위치에 있지 않습니다."

class HangeulRegex:
    def __init__(self, onset, nucleus, coda, multiprocess):
        self.onset = onset # 초성
        self.nucleus = nucleus # 중성
        self.coda = coda # 종성
        self.multiprocess = multiprocess

        self.word_combination = []
        self.common_regex = ""

        # search for all Hangeul word
        if not self.onset and not self.nucleus and not coda:
            self.common_regex = "가-힣"
        # make specific common regex
        else:
            if multiprocess:
                num_cores = multiprocessing.cpu_count()
                print("num_cores = %d" % (num_cores))

                self.make_combination()

                # preprocssing for making common regex
                # reshape two dimension to one dimension
                self.word_combination = self.word_combination.reshape((self.word_combination.size,))

                # split data for multiprocessing
                splited_word_combination = np.array_split(self.word_combination, num_cores)

                # multiprocessing for making common regex
                self.common_regex = parmap.map(self.make_combination, splited_word_combination, pm_pbar=True, pm_processes=num_cores)
            else:
                self.make_combination()
                self.make_common_regex()
                self.common_regex = self.common_regex[:-1]

        # print(self.common_regex)
        
    def get_regex(self):
        return self.common_regex
    def make_common_regex(self, word_combination=None):
        if self.multiprocess:
            common_regex = ""
            for idx1 in range(word_combination.size):
                for idx2 in range(word_combination.size):
                    if idx1 == idx2:
                        common_regex += "(" + word_combination[idx1] + ")+|"
                    else:
                        common_regex += "(" + word_combination[idx1] + ")(" + word_combination[idx2] + ")+|"
                        common_regex += "(" + word_combination[idx2] + ")(" + word_combination[idx1] + ")+|"
            return common_regex
        else:
            print(self.word_combination)
            for idx1 in range(len(self.word_combination)):
                for idx2 in range(len(self.word_combination)):
                    if idx1 == idx2:
                        self.common_regex += "(" + self.word_combination[idx1] + ")+|"
                    else:
                        self.common_regex += "(" + self.word_combination[idx1] + ")(" + self.word_combination[idx2] + ")+|"
                        self.common_regex += "(" + self.word_combination[idx2] + ")(" + self.word_combination[idx1] + ")+|"
                
    def make_combination(self): 
        # print(onset, nucleus, coda)
        # if there's no input in onset
        if not self.onset:
            self.onset = []
            for char in jaso.onsets:
                self.onset.append(char)

        # if there's no input in nucleus
        if not self.nucleus:
            self.nucleus = []
            for char in jaso.nuclei:
                self.nucleus.append(char)
                
        # if there's no input in coda
        if not self.coda:
            self.coda = []
            for char in jaso.codas:
                self.coda.append(char)
                
        if self.multiprocess:
            num_cores = multiprocessing.cpu_count()
            print("num_cores = %d" % (num_cores))

            # preprocessing for making combination
            # split data for multiprocessing
            splited_onset = np.array_split(self.onset, num_cores)
            splited_onset = [item.tolist() for item in splited_onset]

            splited_nucleus = np.array_split(self.nucleus, num_cores)
            splited_nucleus = [item.tolist() for item in splited_nucleus]

            splited_coda = np.array_split(self.coda, num_cores)
            splited_coda = [item.tolist() for item in splited_coda]

            # print(splited_onset, splited_nucleus, splited_coda)
            
            # multiprocessing for making combination
            # word_combination = [ [first thread's result], [second thread's result], ... ]
            # self.word_combination = parmap.starmap(self._combination_workder, splited_onset, splited_nucleus, splited_coda,
            #     jaso.onsets, jaso.nuclei, jaso.codas, pm_pbar=True, pm_processes=num_cores)
            pool = Pool(num_cores)
            self.word_combination = pool.starmap(self._combination_workder, zip(splited_onset, splited_nucleus, splited_coda,
                jaso.onsets, jaso.nuclei, jaso.codas))
        else:
            self.word_combination = self._combination_workder(self.onset, self.nucleus, self.coda, jaso.onsets, jaso.nuclei, jaso.codas)
            print(self.word_combination)

    def _combination_workder(self, onset, nucleus, coda, onsets, nuclei, codas):
        word_combination = []
    
        print("onset = ", onset)
        print("nucleus = ", nucleus)
        print("coda = ", coda)
        print()

        for on in onset:
            for nu in nucleus:
                for cd in coda:
                    # calculate ordering in unicode
                    # onset 
                    #  ㄱ = AC00, first
                    #  ㄴ = AC01, second...

                    # nucleus 
                    # ㅏ = 314F, first
                    # ㅐ = 3150, second ...

                    # coda
                    # using jaso.codas ordering
                    
                    # print(on, nu, cd)
                    on_num = onsets.index(on)
                    nu_num = nuclei.index(nu)
                    cd_num = codas.index(cd)

                    # print(on_num, nu_num, cd_num)
                
                    # print('{:#x}'.format(on_num), '{:#x}'.format(nu_num), '{:#x}'.format(cd_num))
                    word_combination.append(jaso.compose(on_num, nu_num, cd_num))

        return word_combination

class Regex:
    def __init__(self, input_regex, multiprocess):
        self.input_regex = input_regex
        self.multiprocess = multiprocess
        self.output_regex = ""

        self.HangeulRegex_list = []        
        self.lock = Lock()
        self.q = Queue()

        self.make_HangeulRegex()
    def _worker(self, lock, q, onset, nucleus, coda, num):
        regex = HangeulRegex(onset, nucleus, coda, self.multiprocess)
        
        lock.acquire()
        try:
            q.put((num, regex.get_regex(),))
        finally:
            lock.release()
        
    def make_HangeulRegex(self):
        angle_bracket_stack = []
        regex_start = 1
        regex_end = 2

        onset = []
        nucleus = []
        coda = []
        
        # 0 = "<", 1 = 초성, 2 = 중성, 3 = 종성, 4 = ">"
        syllable_flag = 0

        # 0 < comma_count <= 2
        comma_count = 0
    
        try:
            for target in self.input_regex: 
                # check current character is angle bracket
                angle_bracket_flag = self.check_angle_bracket(target, angle_bracket_stack)
                if angle_bracket_flag:
                    # check current character is right or left angle bracket
                    if angle_bracket_flag == regex_start:
                        syllable_flag += 1
                        # print("start bracket")
                    elif angle_bracket_flag == regex_end:
                        syllable_flag = 0 
                        
                        # end of the Hangeul regex, make common regex of one word
                        if self.multiprocess:
                            self.HangeulRegex_list.append(None)
                            self.HangeulRegex_list[-1] = Process(target=self._worker, args=(self.lock, self.q, onset, nucleus, coda, len(self.HangeulRegex_list)))
                            self.HangeulRegex_list[-1].start()
                        else:
                            self.HangeulRegex_list.append(HangeulRegex(onset, nucleus, coda, self.multiprocess))

                        onset = []
                        nucleus = []
                        coda = []
                        comma_count = 0
                        # print("end bracket")

                else:
                    # check current character is comma
                    comma_flag = self.check_comma(target, syllable_flag)               
                    if comma_flag:
                        comma_count += 1
                        if comma_count > 2:
                            raise CommaError
                        syllable_flag += 1
                        # print("comma!")

                    else:
                        # check current character is Hanguel
                        hangeul_flag = self.check_hangeul(target)
                        if hangeul_flag:
                            # target is choseong
                            if syllable_flag == 1:
                                if target in onset:
                                    raise DuplicateHangeulError                                    
                                elif target in jaso.onsets:
                                    onset.append(target)
                                else:
                                    raise NotCorrectLocationHangeulError
                            # target is jungseong
                            elif syllable_flag == 2:
                                if target in nucleus:
                                    raise DuplicateHangeulError
                                elif target in jaso.nuclei:
                                    nucleus.append(target)
                                else:
                                    raise NotCorrectLocationHangeulError
                                # target is jongseong
                            elif syllable_flag == 3:
                                if target in coda:
                                    raise DuplicateHangeulError
                                elif target in jaso.codas:
                                    coda.append(target)
                                else:
                                    raise NotCorrectLocationHangeulError

                            # print("Hangeul!")
                        else:
                            raise NotHangeulError
                
                # print(syllable_flag)
                
            # 모든 syntax check 후에도 angle_bracket_stack에 정보가 남아있다면
            # = syntax error
            if angle_bracket_stack:
                raise AngleBracketError
        except AngleBracketError as error:
            print(error)
            return False
        except CommaError as error:
            print(error)
            return False
        except NotHangeulError as error:
            print(error)
            return False
        except DuplicateHangeulError as error:
            print(error)
            return False
        except NotCorrectLocationHangeulError as error:
            print(error)
            return False

        self.merge_regex()

    def get_regex(self):
        return self.output_regex

    # merge regex to common regex
    def merge_regex(self):
        self.output_regex += "/"

        if self.multiprocess:
            input_regex_num = len(self.HangeulRegex_list)
            queue_count = input_regex_num

            mp_regex_list = []

            # pop all value in queue
            while queue_count > 0:
                queue_count -= 1
                mp_regex_list.append(self.q.get())

            mp_regex_list.sort(key = operator.itemgetter(0))

            for regex in mp_regex_list:
                self.output_regex += "(" + regex[1] + ")"
        else:
            for regex in self.HangeulRegex_list:
                self.output_regex += "(" + regex.get_regex() + ")"
        
        self.output_regex += "/g"

    def check_hangeul(self, target):
        hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7FF]+', target))

        return hanCount > 0

    def check_comma(self, target, syllable_flag):
        if target != ",":
            return False
        
        # comma is out of regex
        if syllable_flag == 0 or syllable_flag == 4:
            raise CommaError

        # target is comma!
        return True
        

    def check_angle_bracket(self, target, angle_bracket_stack):
        #  return False = No angle bracket
        #  return 1 = start bracket
        #  return 2 = end bracket

        if target != "<" and target != ">":
            return False
        else:
            # is list empty?

            # list is empty
            if not angle_bracket_stack:
                # angle bracket error
                if target == ">":
                    raise AngleBracketError
                # noraml : append "<" to stack
                else:
                    angle_bracket_stack.append(target)
                    return 1
            # list isn't empty
            else:
                # angle bracket error
                if target == "<":
                    raise AngleBracketError
                else:
                    angle_bracket_stack.pop()
                    return 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hangeul Regex Contructor')

    parser.add_argument('-m', dest="multiprocess", help="computing using multiprocessing", action='store_true')
    parser.set_defaults(multiprocess=False)

    parser.add_argument('regex', type=str,
                    help="<초성, 중성, 종성>의 형식으로 입력")
                    
    args = parser.parse_args()

    print(args)
    start_time = time.time()
    regex = Regex(args.regex, args.multiprocess)
    end_time = time.time()

    print("elapsed time = %sms" % ((end_time - start_time) * 1000))
    print(regex.get_regex())