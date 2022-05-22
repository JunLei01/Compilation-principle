#-*- coding : utf-8-*-
from graphviz import Digraph

global States       #  nfa中的状态集合
global Sigmas       #  nfa中的符号集合（不含ε）
_closure0 = []      #  nfa中的初始状态
temp_closure = []   #  暂存产生的状态

#  读取NFA的相关数据
def read_data(path):
    nfa = []
    with open(path, 'r') as fp:
        data = [line.rstrip('\n') for line in fp.readlines()]
    begin = data[0]             #  记录开始状态
    end = data[1]               #  记录结束状态
    nfa = data[2::]
    for i in range(len(nfa)):
        nfa[i] = nfa[i].split()       #  将数据按空格切分开，并保存在nfa中
    return nfa, begin, end

#  绘制NFA的图像
def draw_NFA(nfa, begin, end):
    image = Digraph('G', filename='NFA.gv', format='png')
    for node in nfa:
        if node[1] == 'E':
            node[1] = chr(949)
        image.edge(node[0], node[2], label=node[1])
    image.node(begin, color='red')
    image.node(end, shape='doublecircle')
    image.view()

#  读取nfa中所有的状态
def get_states(nfa):
    global States, Sigmas
    states = []
    sigmas = []
    for i in nfa:
        states.append(i[0])
        states.append(i[2])
        sigmas.append(i[1])
    States = list(set(states))
    Sigmas = list(set(sigmas))
    if 'E' in Sigmas:
        Sigmas.remove('E')
    States.sort(key=states.index)       #   nfa中所有的状态集合
    Sigmas.sort(key=sigmas.index)       #   nfa中所有的符号集合（不含ε）

#  递归使用深度搜索算法，寻找nfa中只通过ε能到达的所有状态
def init_closure(begin, nfa):
    if begin in _closure0:
        return False                #  如果当前状态已经存在于初始状态集合中则结束递归
    _closure0.append(begin)         #
    for change in nfa:
        if change[0] == begin and change[1] == 'E':    #  如果遇到ε则继续向下寻找下去
            init_closure(change[2], nfa)
        if change[0] == begin and change[1] != 'E':
            continue
    return True

def find2_closure(begin, nfa):
    if begin in _closure0:
        return False                #  如果当前状态已经存在于初始状态集合中则结束递归
    _closure0.append(begin)         #
    for change in nfa:
        if change[0] == begin and change[1] == 'E':    #  如果遇到ε则继续向下寻找下去
            init_closure(change[2], nfa)
        if change[0] == begin and change[1] != 'E':
            continue
    return True

def find_closure(begin, nfa, sigma):
    print(begin, sigma)
    if begin in temp_closure:
        return False
    temp_closure.append(begin)
    for change in nfa:
        if change[0] == begin and (change[1] == 'E' or change[1] == sigma):
            find_closure(change[2], nfa, sigma)
        if change[0] == begin and (change[1] != 'E' or change[1] != sigma):
            continue
    return True

def E_closure(closure, nfa, sigma):
    temp_closure.clear()
    for state in closure:
        for i in range(len(nfa)):
            if state == nfa[i][0] and (sigma == nfa[i][1]):
                if state not in temp_closure:
                    temp_closure.append(state)
                find_closure(nfa[i][2], nfa, sigma)
            if state == nfa[i][0] and (nfa[i][1] == 'E'):
                if state not in temp_closure:
                    temp_closure.append(state)
                find2_closure(nfa[i][2], nfa, sigma)
            if temp_closure:
                if state == closure[-1]:
                    return temp_closure

#  将NFA转换为DFA
def NFA_to_DFA(_closure0):
    all_closure = []
    dfa = []
    _closure = []
    #  NFA转DFA
    i = 0
    while _closure:
        begin = _closure.pop(0)
        for sigma in Sigmas:
            temp = E_closure(begin, nfa, sigma)
            if temp not in all_closure:
                _closure.append(temp[:])
                # print("c_closure", _closure)
                all_closure.append(temp[:])
            if temp in all_closure:
                start = "closure" + str(i)
                end = "closure" + str(all_closure.index(temp))
                dfa.append([start, sigma, end])
        i += 1
    strat = "closure0"
    end = "closure" + str(i-1)
    draw_DFA(dfa, strat, end)
    return dfa


def draw_DFA(dfa, begin, end):
    image = Digraph('G', filename='DFA.gv', format='png')
    for node in dfa:
        image.edge(node[0], node[2], label=node[1])
    image.node(begin, color='red')
    image.node(end, shape='doublecircle')
    image.view()

#   替换Dtran中的相同状态
def replace(state, closure):
    new_closure = []
    for list in closure:
        if type(list).__name__ == 'list':
            new_list = []
            for x in list:
                if x in state:
                    new_list.append(state[0])
                else:
                    new_list.append(x)
            new_closure.append(new_list)
        else:
            if list in state:
                new_closure.append(state[0])
        print(new_closure)
    return new_closure

#   化简DFA
def DFA_simplest(dfa):
    Dtran = []
    temp_dtran = []

    #   读取所有的dfa中的所有状态，构建Dtran
    for start in States:
        temp_dtran.clear()
        temp_dtran.append(start)
        for state in dfa:
            if state[0] == start:
                temp_dtran.append(state[1])
                temp_dtran.append(state[2])
        Dtran.append(temp_dtran[:])
    print(Dtran)

    same_closure = []
    shift_dtran = []

    #   寻找相同的状态并删除标记
    for state in Dtran:
        s = []
        s.clear()
        for i in range(1, len(Sigmas)+1):
            s.append(state[2*i])
        if s not in shift_dtran:
            shift_dtran.append(s)
            shift_dtran.append(state[0])
        else:
            same = (shift_dtran[shift_dtran.index(s) + 1], state[0])
            same_closure.append(same)
    fianl_same = []
    fianl_same.append(same_closure[0][0])

    #   将Dtran中的相同的状态转化
    for state in same_closure:
        if state[0] in fianl_same:
            fianl_same.append(state[1])
        if state[1] in fianl_same:
            fianl_same.append(state[0])
        if state[0] not in fianl_same and state[1] not in fianl_same:
            continue
    fianl_same = list(set(fianl_same))
    shift_dtran = replace(fianl_same, shift_dtran)

    #   返回最简状态
    return shift_dtran

#  绘制最简图
def draw_simplest(dtran):
    image = Digraph('G', filename='simplest.gv', format='png')
    for state in dtran:
        image.edge(state[0], state[2], label=state[1])
    image.node(dtran[0][0], shape='doublecircle')
    image.view()


if __name__ == '__main__':
    all_closure = []
    dfa = []
    _closure = []
    data_path = '/compilation_principle/experiment2/data.txt'
    nfa, begin, end = read_data(data_path)
    draw_NFA(nfa, begin, end)
    get_states(nfa)
    init_closure(begin, nfa)
    _closure.append(_closure0)
    all_closure.append(_closure0)
    #  NFA转DFA
    dfa = NFA_to_DFA(_closure0)
    #  化简DFA
    shift_dtran = DFA_simplest(dfa)
    #  绘制最简的图像
    draw_simplest(shift_dtran)