#-*- coding: utf8 -*-
import argparse
import re
import sys
import os

# ../src/tagger/nlp/jaso.py
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from src.tagger.nlp import jaso

import time
from multiprocessing import Process, Lock, Queue, Pool
import multiprocessing
import parmap
from tqdm import tqdm

import operator
import numpy as np
from itertools import product
from itertools import repeat
from itertools import chain

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

class NotCorrectLocationAtError(Exception):
    def __str__(self):
        return "'@'가 올바른 위치에 있지 않습니다."

class DuplicateAtError(Exception):
    def __str__(self):
        return "중복된 '@'는 허용하지 않습니다."


class HangeulRegex:
    """
    Class for one hangeul regex
    eg. <,,>

    Make hangeul regex to common regex.
    It can use multiprocessing for making combination of hangeul regex.

    Class makes all combination of hangeul regex.
    eg. Combination of <ㄱ,ㅏ,> is "가, 각, 갂, ..., 갛"

    Attributes:
        onset : 
            A string indicating onset of hangeul regex.
        nucleus : 
            A string indicating nucleus of hangeul regex.
        coda : 
            A string indicating coda of hangeul regex.
        multiprocess : 
            A boolean indicating using multiprocessing or not.
    """
    def __init__(self, onset, nucleus, coda, multiprocess):
        """ Inits HangeulRegex """
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
                # Making combination of hangeul regex using multiprocessing
                self.make_combination()

                """
                Preprocssing for making common regex.

                Split word_combination list and distribute to each thread.
                """
                num_cores = multiprocessing.cpu_count()
                
                # Result of multiprocessing is iteralbe.
                # So, convert to list.
                self.word_combination = list(chain.from_iterable(self.word_combination))

                # Split data for multiprocessing.
                splited_word_combination = np.array_split(self.word_combination, num_cores)

                # Multiprocessing using splited data.
                # Get a common regex for one hangeul regex
                self.common_regex = parmap.map(self.make_common_regex, splited_word_combination, pm_pbar=True, pm_processes=num_cores)

                # Convert common_regex which is 1d list to a string
                temp_string = ""
                for regex in self.common_regex:
                    temp_string += regex
                self.common_regex = temp_string
            else:
                """
                Making common regex using single thread
                """
                self.make_combination()
                self.make_common_regex()

                # Last word of common_regex must be "|".
                # It is not what we want, so remove it.
                self.common_regex = self.common_regex[:-1]
        
    def get_regex(self):
        return self.common_regex

    def make_common_regex(self, word_combination=None):
        """

        Make common regex from all word combination.

        Args:
            word_combination:
                Default value is None.
                When using single thread, this argument must be None.
                When using multi thread, this argument is one of splited word_combination.
        
        Returns:
            When using single thread, return is not define.
            When using multi thread, return common regex of word_combination.
        """
        if self.multiprocess:
            common_regex = ""
            for word in word_combination:
                    # Purpose of common regex is just find a word.
                    # So, type of regex is ({Hangeul word})+|
                    common_regex += "(" + word + ")+|"
                    
            return common_regex
        else:
            for word in self.word_combination:
                self.common_regex += "(" + word + ")+|"
                
                
    def make_combination(self): 
        """
        Making all combination from set of onset, nucleus, coda.
        
        Result is saved at self.word_combination
        """

        # True if set of onset is empty
        if not self.onset:
            # Saving all onset in self.onset
            self.onset = []
            for char in jaso.onsets:
                self.onset.append(char)

        # True if set of nucleus is empty
        if not self.nucleus:
            # Saving all nucleus in self.nucleus
            self.nucleus = []
            for char in jaso.nuclei:
                self.nucleus.append(char)
                
        # True if set of coda is empty
        if not self.coda:
            # Saving all coda in self.coda
            self.coda = []
            for char in jaso.codas:
                self.coda.append(char)
                
        if self.multiprocess:
            num_cores = multiprocessing.cpu_count()

            """
            Preprocssing for making common regex.

            Let X is set of onset, nucleus, coda.
            Split two set of X and distribute to each thread.
            eg. Split onset, nucleus or nucleus, coda or onset, coda

            """
            splited_onset = None
            splited_nucleus = None
            splited_coda = None

            # Find longest set and split longest set.
            # Split longest set is good for performance.
            if len(self.onset) >= len(self.nucleus) and len(self.onset) >= len(self.coda):
                # onset is longest

                # Split onset
                splited_onset = np.array_split(self.onset, num_cores)

                # Convert each ndarray item to list
                # Because _combination_worker function use <list>.index()
                splited_onset = [item.tolist() for item in splited_onset]

                with Pool(num_cores) as pool:
                    self.word_combination = pool.starmap(self._combination_workder, zip(splited_onset, repeat(self.nucleus), repeat(self.coda),
                    repeat(jaso.onsets), repeat(jaso.nuclei), repeat(jaso.codas)))
            elif len(self.nucleus) >= len(self.onset) and len(self.nucleus) >= len(self.coda):
                # nucleus is longest

                # Split nucleus
                splited_nucleus = np.array_split(self.nucleus, num_cores)

                # Convert each ndarray item to list
                # Because _combination_worker function use <list>.index()
                splited_nucleus = [item.tolist() for item in splited_nucleus]

                with Pool(num_cores) as pool:
                    self.word_combination = pool.starmap(self._combination_workder, zip(repeat(self.onset), splited_nucleus, repeat(self.coda),
                    repeat(jaso.onsets), repeat(jaso.nuclei), repeat(jaso.codas)))
            else:
                # coda is longest
                splited_coda = np.array_split(self.coda, num_cores)

                # Convert each ndarray item to list
                # Because _combination_worker function use <list>.index()
                splited_coda = [item.tolist() for item in splited_coda]

                with Pool(num_cores) as pool:
                    self.word_combination = pool.starmap(self._combination_workder, zip(repeat(self.onset), repeat(self.nucleus), splited_coda,
                    repeat(jaso.onsets), repeat(jaso.nuclei), repeat(jaso.codas)))
        else:
            # Single thread
            # Call _combination_worker one time.
            self.word_combination = self._combination_workder(self.onset, self.nucleus, self.coda, jaso.onsets, jaso.nuclei, jaso.codas)

    def _combination_workder(self, onset, nucleus, coda, onsets, nuclei, codas):
        """
        Making word set using onset, nucleus, coda.
        Word set contains all posibile combination of onset, nucleus, coda.

        Args:
            onset: A list of possible onset
            nucleus: A list of possible nucleus
            coda: A list of possible coda

            onset : A list of all onset
            nucleus: A list of all nucleus
            coda: A list of all coda
        
        Returns:
            A list which contains all possible combination of onset, nucleus, coda.
        """
        word_combination = []

        for on in tqdm(onset, desc="calculating combination :"):
            for nu in nucleus:
                for cd in coda:
                    # Calculate ordering in unicode
                    # 
                    # onset 
                    #  ㄱ = \uAC00, first
                    #  ㄴ = \uAC01, second ...
                    # 
                    # nucleus 
                    # ㅏ = \u314F, first
                    # ㅐ = \u3150, second ...
                    # 
                    # coda
                    # Using jaso.codas ordering, not unicode ordering.
                    # Because unicode contains some older Hangeul.
                    
                    on_num = onsets.index(on)
                    nu_num = nuclei.index(nu)

                    # '@' means first order of codas.
                    if cd == '@':
                        cd_num = 0
                    cd_num = codas.index(cd)

                    # Making a word using jaso.compose
                    word_combination.append(jaso.compose(on_num, nu_num, cd_num))

        return word_combination

class Regex:
    """
    Class contain all <HangeulRegex>
    eg. Class conatin <,,><,,>....<,,>.

    Checking syntax of input Hangeul regex.
    Making common regex from <HangeulRegex> and merge it.
    """
    def __init__(self, input_regex, multiprocess, remove_slash_and_flag):
        """ Inits Regex """
        self.input_regex = input_regex
        self.multiprocess = multiprocess
        self.output_regex = ""
        self.remove_slash_and_flag = remove_slash_and_flag

        # List of all regex
        self.HangeulRegex_list = []        

        # Lock for queue
        self.lock = Lock()

        # Queue contains result of <HangeulRegex>
        self.q = Queue()

        # Get boolean flag Hangeul regex is validated.
        self.regex_validation = self.make_HangeulRegex()
            

    def _worker(self, lock, q, onset, nucleus, coda, num):
        """
        Define a HangeulRegex object and get common regex.

        Args:
            lock : A lock object for q.
            q : A queue object to save result of <HangeulRegex>.
            onset : A list of onset.
            nucleus : A list of nucleus.
            coda : A list of coda.
            num : A integer indicates ordering of regex.

        Returns
            Not define
        """
        regex = HangeulRegex(onset, nucleus, coda, self.multiprocess)
        
        lock.acquire()
        try:
            q.put((num, regex.get_regex(),))
        finally:
            lock.release()
        
    def make_HangeulRegex(self):
        """
        Validate input regex.
        Execute multi thread.

        Returns
            A boolean indicates regex is validated.

        Raises:
            AngleBracketError : 
                An error occured when using angle bracket at wrong location or wrong angle bracket.
            CommaError :
                An error occured when using comma not 2 times or wrong location.
            NotHangeulError :
                An error occured when not using Hangeul.
            DuplicateHangeulError :
                An error occured when using duplicated word.
            NotCorrectLocationHangeulError as error:
                An error occured when using hangeul at wrong location.
                eg. <,ㄱ,> : Onset is not located at location of onset.
            NotCorrectLocationAtError as error:
                An error occured when using '@' at wrong location.
        """
        angle_bracket_stack = []
        regex_start = 1
        regex_end = 2

        onset = []
        nucleus = []
        coda = []
        
        # 0 = "<", 1 = onset, 2 = nucleus, 3 = coda, 4 = ">"
        syllable_flag = 0

        # 0 < comma_count <= 2
        comma_count = 0

        # Must be zero or one.
        at_count = 0
    
        try:
            # target is a charcter.
            for target in self.input_regex: 
                # Check current character is angle bracket.
                angle_bracket_flag = self.check_angle_bracket(target, angle_bracket_stack)

                if angle_bracket_flag:
                    # If current character is right angle bracket, it is start point of Hangeul regex.
                    # If current character is left angle bracket, it is end point of Hangeul regex.
                    if angle_bracket_flag == regex_start:
                        syllable_flag += 1
                    elif angle_bracket_flag == regex_end:
                        syllable_flag = 0 
                        
                        # End of the Hangeul regex, make common regex of one word
                        if self.multiprocess:
                            self.HangeulRegex_list.append(None)
                            self.HangeulRegex_list[-1] = Process(target=self._worker, args=(self.lock, self.q, onset, nucleus, coda, len(self.HangeulRegex_list)))
                            self.HangeulRegex_list[-1].start()
                        else:
                            self.HangeulRegex_list.append(HangeulRegex(onset, nucleus, coda, self.multiprocess))

                        # Clear for new Hangeul regex
                        onset = []
                        nucleus = []
                        coda = []
                        comma_count = 0

                else:
                    # Check current character is comma
                    comma_flag = self.check_comma(target, syllable_flag)               

                    if comma_flag:
                        comma_count += 1

                        if comma_count > 2:
                            raise CommaError

                        syllable_flag += 1

                    else:
                        # Check current character is Hanguel
                        hangeul_flag = self.check_hangeul(target)

                        if hangeul_flag:
                            # True if current character is onset.
                            if syllable_flag == 1:
                                if target in onset:
                                    raise DuplicateHangeulError
                                elif target == '@':
                                    raise NotCorrectLocationAtError                                    
                                elif target in jaso.onsets:
                                    onset.append(target)
                                else:
                                    raise NotCorrectLocationHangeulError
                            # True if current character is nucleus.
                            elif syllable_flag == 2:
                                if target in nucleus:
                                    raise DuplicateHangeulError
                                elif target == '@':
                                    raise NotCorrectLocationAtError
                                elif target in jaso.nuclei:
                                    nucleus.append(target)
                                else:
                                    raise NotCorrectLocationHangeulError
                            # True if current character is coda.
                            elif syllable_flag == 3:
                                if target in coda:
                                    raise DuplicateHangeulError
                                elif target == '@' and at_count == 1:
                                    raise DuplicateAtError
                                elif target in jaso.codas:
                                    coda.append(target)
                                else:
                                    raise NotCorrectLocationHangeulError
                        else:
                            raise NotHangeulError
                
            # True if stack is not empty.
            # If flag is true, angle bracket syntax error
            # eg. "<>>", "<<>", "<"
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
        except NotCorrectLocationAtError as error:
            print(error)
            return False

        self.merge_regex()
        return True
        

    def get_regex(self):
        if self.regex_validation:
            return self.output_regex
        else:
            return "Check regex is correct."

    def merge_regex(self):
        """
        Merge split regex to one regex
        """

        if not self.remove_slash_and_flag:
            self.output_regex += "/"

        if self.multiprocess:
            input_regex_num = len(self.HangeulRegex_list)
            queue_count = input_regex_num

            mp_regex_list = []

            # Pop all value in queue and save.
            while queue_count > 0:
                queue_count -= 1
                mp_regex_list.append(self.q.get())

            # Value of q : (ordering number, regex)
            # Sort by first element of value.
            mp_regex_list.sort(key = operator.itemgetter(0))

            # Save only regex(string)
            for regex in mp_regex_list:
                self.output_regex += regex[1]

            # ouut_regex's last word is "|", so remove it.
            self.output_regex = self.output_regex[:-1]
        else:
            # Single thread case, just merge all regex string.
            for regex in self.HangeulRegex_list:
                self.output_regex += regex.get_regex()
        
        if not self.remove_slash_and_flag:
            self.output_regex += "/g"

    def check_hangeul(self, target):
        """
        Check input argument is Hangeul or '@'.

        Args:
            target : A character indicates one character in input regex.
        
        Returns:
            True, if target is Hangeul or '@'.
            False, if target is not Hangeul and '@'.
        """
        # Check target string is Hangeul.
        # \u3130='ㄱ', \u318F='last Hangeul compatibility jamo'
        # \uAC00='가', \uD7FF='last Hangeul jamo extended-B'
        # Coda should allow '@'.
        hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7FF]+|[\@]', target))

        return hanCount > 0

    def check_comma(self, target, syllable_flag):
        """
        Check input argument 'target' is comma.

        Args : 
            target : A character indicates one character in input regex.
            syllable_flag : 0 = "<", 1 = onset, 2 = nucleus, 3 = coda, 4 = ">"

        Returns :
            True, if target is comma.
            False, if target is not comma.
        """
        if target != ",":
            return False
        
        # Comma is out of regex range.
        if syllable_flag == 0 or syllable_flag == 4:
            raise CommaError

        # target is comma!
        return True
        

    def check_angle_bracket(self, target, angle_bracket_stack):
        """
        Check target is angle bracket.
        If target is angle bracket, check angle bracket is located in right location.

        Args:
            target : A character indicates one character in input regex.
            angle_bracket_stack :
                A stack, push value when target is start anlge bracket(<), pop value when target is end angle bracket(>).

        Returns :
            False, if target is not angle bracket.
            1, if target is start bracket(<).
            2, if target is end bracket(>).
        """
        

        if target != "<" and target != ">":
            return False
        else:
            # True, if stack is empty.
            if not angle_bracket_stack:
                # True, if angle bracket ordering is wrong.
                # When stack is empty, target must be "<".
                if target == ">":
                    raise AngleBracketError
                else:
                    # Noraml case, so append "<" to stack.
                    angle_bracket_stack.append(target)
                    return 1
            else:
                # True, if angle bracket ordering is wrong.
                # When stack is not empty, target must be ">".
                if target == "<":
                    raise AngleBracketError
                else:
                    angle_bracket_stack.pop()
                    # Noraml case, so pop.
                    return 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hangeul Regex Contructor')

    parser.add_argument('-m', dest="multiprocess", help="computing using multiprocessing", action='store_true')
    parser.add_argument('-r', dest="remove_slash_and_flag", help="remove slash and global flag to copy&paste in editor research", action='store_true')

    parser.set_defaults(multiprocess=False)
    parser.set_defaults(remove_slash_and_flag=False)

    parser.add_argument('regex', type=str,
                    help="<초성, 중성, 종성>의 형식으로 입력")
                    
    args = parser.parse_args()

    print(args)
    start_time = time.time()
    regex = Regex(args.regex, args.multiprocess, args.remove_slash_and_flag)
    end_time = time.time()

    print("elapsed time = %sms" % ((end_time - start_time) * 1000))
    
    with open("Hangeul_regex.txt", 'w') as output_file:
        output_file.write(regex.get_regex()) 