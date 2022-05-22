import csv
import pandas as pd
from itertools import chain

class grammar(object):
    def __init__(self):
        self.grammar = []
        self.vt = []
        self.vn = []
        self.terminators = []
        self.first = []
        self.follow = []
        self.temp = []
        self.vn_final = []
        self.ana_table = []
        self.next = []

    #  读取文法数据
    def read_data(self):
        with open("data/gramma.txt", 'r') as fp:
            data = [line.rstrip('\n') for line in fp.readlines()]
        with open("data/terminator.txt", 'r') as fp:
            terminators = [line.rstrip('\n') for line in fp.readlines()]

        for i in range(len(data)):
            data[i] = data[i].split()
            self.grammar.append(data[i])
        for i in range(len(terminators)):
            self.terminators += (terminators[i].split())

    #  切分列表
    def deal(self,list_ori, p):
        list_new = []
        list_short = []
        for i in list_ori:
            if i != p:
                list_short.append(i)
            else:
                list_new.append(list_short)
                list_short = []
        list_new.append(list_short)
        return list_new

    #   数据处理
    def data_processing(self):
        for i in self.grammar:
            self.vn.append(i[0])
        self.vn = list(set(self.vn))
        gg = []
        for sencente in self.grammar:
            tem = self.deal(sencente, '|')
            gx = [sencente[0], sencente[1]]
            i = 0
            while tem:
                x = tem.pop(0)
                if i == 0:
                    gg.append(x)
                else:
                    gx += x
                    gg.append(gx)
                i += 1
        self.grammar.clear()
        self.grammar = gg
        self.vn_final = self.vn

    #   构建first集合
    def find_first(self, symbol):
        for sencente in self.grammar:
            if sencente[0] == symbol:
                if sencente[2] in self.terminators or sencente[2].startswith("'"):
                    self.vt.append(sencente[2])
                    self.temp.append(sencente[2])
                else:
                    self.find_first(sencente[2])

    def follow_analysis(self):
        while self.vn:
            self.temp.clear()
            self.temp.append(symbol)
            self.find_follow(symbol)
            self.first.append(self.temp[:])

    #   对FOLLOW的三种情况进行集合加入操作
    def collection_replication(self, head, first, flag):
        # print(head, "first:", first, flag)
        if flag == "first":
            for element in self.first:
                if element[0] == first:
                    for x in element[1:]:
                        if x == chr(949):
                            self.collection_replication(head, first, "follow")
                        else:
                            self.temp.append(x)
                    return True
        if flag == "follow":
            if not self.follow:
                return False
            for element in self.follow:
                if element[0] == head and len(element) > 1:
                    self.temp += element[1:]
                    return True
                if element[0] == head and len(element) == 1:
                    return False

    #   判断当前集合是否为空
    def judge_is_empty(self, x):
        for element in self.first:
            if element[0] == x:
                if chr(949) in element and len(element) == 2:
                    return True
                if len(element) > 2:
                    return False

    #   构建FOLLOW集合
    def find_follow(self, symbol):
        for element in self.grammar:
            for i in range(len(element[1:])):
                if element[i+1] == symbol:
                    position = i + 1
                    print(symbol, position, element)
                    #   判断是否属于情况三
                    if (position+1) < len(element):
                        x = element[position + 1]
                        if x in self.terminators or x.startswith("'"):
                            self.temp.append(x)
                            continue
                        if self.judge_is_empty(x):
                            flag = self.collection_replication(element[0], element[0], "follow")
                            if not flag:
                                return False
                        if x != "|":
                            flag = self.collection_replication(element[0], x, "first")
                            if not flag:
                                return False
                    #   判断是否属于情况二
                    if (position+1) == len(element):
                        flag = self.collection_replication(element[0], element[0], "follow")
                        if not flag:
                            return False
                    # print("temp:", self.temp)
        return True

    #   构建文法分析表
    def analysis_table(self):
        row_data = []
        for non_terminator in self.vn:
            row_data.clear()
            row_data.append(non_terminator)
            for element in self.grammar:
                if element[0] == non_terminator:
                    if element[2] in self.vt and element[2] != chr(949):    #   判断是否属于情况二
                        tem = {element[2]: element[2:]}
                        row_data.append(tem)
                    elif element[2] == chr(949):    #   判断左推导首项是否属于情况三
                        for follow in self.follow:
                            if follow[0] == non_terminator:
                                for sym in follow[1:]:
                                    tem = {sym: element[2:]}
                                    row_data.append(tem)
                    else:   #   判断左推导首项是否属于情况一
                        for first in self.first:
                            if first[0] == non_terminator:
                                for sym in first[1:]:
                                    if sym != chr(949):
                                        tem = {sym: element[2:]}
                                        row_data.append(tem)
                                    else:
                                        for follow in self.follow:
                                            if follow[0] == non_terminator:
                                                for sym in follow[1:]:
                                                    tem = {sym: element[2:]}
                                                    row_data.append(tem)
            self.ana_table.append(row_data[:])

    #   获取当前的操作动作
    def get_act(self, t, target):
        self.next.clear()
        for element in self.ana_table:
            if element[0] == t:
                for next in element[1:]:
                    if list(next.keys())[0] == target:
                        self.next.extend(list(next.values())[0])

    #   预测分析过程
    def predict(self, string):
        string = string.split()
        work_stack = ["$"]
        work_stack.append("X")
        print(work_stack, string)
        while string:
            target = string.pop(0)
            while work_stack:
                t = work_stack.pop()
                print("匹配: ", t, target)
                if t != target:
                    self.get_act(t, target)
                    while self.next:
                        x = self.next.pop()
                        if x != chr(949):
                            work_stack.append(x)
                else:
                    break
                print(work_stack, "    ", string)

if __name__ == '__main__':
    predict_string = input()
    grammar_analysis = grammar()
    grammar_analysis.read_data()
    grammar_analysis.data_processing()

    print(grammar_analysis.grammar)
    for symbol in grammar_analysis.vn:
        grammar_analysis.temp.clear()
        grammar_analysis.temp.append(symbol)
        grammar_analysis.find_first(symbol)
        grammar_analysis.first.append(grammar_analysis.temp[:])
    print("FIRST:", grammar_analysis.first)
    grammar_analysis.vt = list(set(grammar_analysis.vt))
    grammar_analysis.vt.remove(chr(949))
    grammar_analysis.vt.insert(0, 'non_terminator')
    grammar_analysis.vt.append('$')

    grammar_analysis.follow_analysis()

    grammar_analysis.analysis_table()
    print("FOLLOW:", grammar_analysis.follow)
    print(grammar_analysis.ana_table)

    grammar_analysis.predict(predict_string)