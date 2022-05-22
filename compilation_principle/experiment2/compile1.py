from graphviz import Digraph

class Part:
    def __init__(self, src, edge, dst):
        self.src = src
        self.edge = edge
        self.dst = dst


def check(str, x):
    for i in range(len(str)):
        if str[i]==x:
            return True
    return False


def closure(setp, NFA):
    t = len(setp)
    i = 0
    while i < t:
        for j in range(len(NFA)):
            if setp[i] == NFA[j].src[0] and NFA[j].edge[0]=='&':
                if not check(setp, NFA[j].dst[0]):
                    setp += NFA[j].dst[0]
                    t += 1
        i += 1
    return setp


def move(t, a, NFA):
    temp = ""
    for i in range(len(t)):
        for j in range(len(NFA)):
            if t[i] == NFA[j].src[0] and NFA[j].edge[0]==a:
                if not check(temp, NFA[j].dst[0]):
                    temp += NFA[j].dst[0]
    return temp


def checkINrawDFA(rawDFA, u):
    for i in range(len(rawDFA)):
        if rawDFA[i] == u:
            return True
    return False


def checkFlag(t):
    for i in range(len(t)):
        if t[i]==False:
            return i
    return -1

def checkINdex(rawDFA, u):
    for i in range(len(rawDFA)):
        if rawDFA[i] == u:
            return i
    return -1


NFA = []
NFA2 = []
NFADic = {}
dot = Digraph(comment='The Test Table')
num = int(input('input:'))
for i in range(num):
    x = input()
    y = input()
    z = input()
    temp = []
    temp.append(int(x))
    temp.append(int(z))

    NFA2.append(temp)
    NFADic[tuple(temp)] = y
    temp = Part(x, y, z)
    NFA.append(temp)
    dot.node(x, x)
    dot.edge(x, z, y)

# dot.render('NFA.gv', view=True)
for i in range(len(NFA)):
    print(NFA[i].src, NFA[i].edge, NFA[i].dst)

sigma = ['a', 'b']
start = closure("0", NFA)
start = "".join(sorted(start))
rawDFA = []
rawDFA.append(start)
rawDFAflag = []
rawDFAflag.append(False)
while checkFlag(rawDFAflag) != -1:
    m = checkFlag(rawDFAflag)
    rawDFAflag[m] = True
    for i in range(len(sigma)):
        u = closure(move(rawDFA[m], sigma[i], NFA), NFA)
        u = "".join(sorted(u))
        if not checkINrawDFA(rawDFA, u):
            rawDFA.append(u)
            rawDFAflag.append(False)

DFA = []
DFA2 = []
DFADic = {}

for i in range(len(rawDFA)):
    print(rawDFA[i], closure(move(rawDFA[i], 'a', NFA), NFA), closure(move(rawDFA[i],'b',NFA),NFA))
    DFA.append(rawDFA[i])


dot2 = Digraph(comment='The Test Table')
for i in range(len(DFA)):
    temp = []
    temp.append(i)
    temp.append(checkINdex(rawDFA, "".join(sorted(closure(move(rawDFA[i], 'a', NFA), NFA)))))
    DFA2.append(temp)
    DFADic[tuple(temp)] = 'a'
    temp = []
    temp.append(i)
    temp.append(checkINdex(rawDFA, "".join(sorted(closure(move(rawDFA[i], 'b', NFA), NFA)))))
    DFA2.append(temp)
    DFADic[tuple(temp)] = 'b'
    dot2.node(str(i), str(i))
    dot2.edge(str(i), str(checkINdex(rawDFA, "".join(sorted(closure(move(rawDFA[i], 'a', NFA), NFA))))),'a')
    dot2.edge(str(i), str(checkINdex(rawDFA, "".join(sorted(closure(move(rawDFA[i], 'b', NFA), NFA))))),'b')

dot2.render('DFA.gv', view=True)

#-*- coding : utf-8-*-
from graphviz import Digraph
import re

def graph_nfaprint():  # 画NFA的图像
    g = Digraph('G', filename='NFA.gv', format='png')
    for i in range(len(Move_NFA)):
        g.edge(Move_NFA[i][0], Move_NFA[i][2], label=Move_NFA[i][1])
    for i in range(len(Begin)):
        g.node(Begin[i], color='red')  # 开始节点红色
    for j in range(len(End)):
        g.node(End[j], shape='doublecircle')  # 结束节点双层

    g.view()

def graph_dfaprint(StateList, Begin0, End0):  # 画DFA图像
    g = Digraph('G', filename='DFA.gv', format='png')
    Begin1 = []
    End1 = []
    for i in range(len(Begin0)):
        Begin1.append(" ".join(sorted(Begin0[i])))
    for j in range(len(End0)):
        End1.append(" ".join(sorted(End0[j])))  # 从小到大排序

    for i in range(len(StateList)):
        Dictt = FindNewState(StateList[i])
        for j in Str0:
            if StateList[i] != [] and Dictt[j] != []:
                g.edge(" ".join(sorted(StateList[i])), " ".join(sorted(Dictt[j])), label=j)
    for k in range(len(Begin1)):
        g.node(Begin1[k],color='red', shape='circle')
    for i in range(len(StateList)):
        g.node(" ".join(sorted(StateList[i])), shape='circle')
    for j in range(len(End1)):
        g.node(End1[j], shape='doublecircle')
    g.view()


def Findclosure(AA):   # 输入一个状态,找这个状态的所有等价状态
    A = _closure[AA]   # 查询输入状态的空闭包
    A0 = []
    for ch in A:
        A0 = A0 + _closure[ch]
    A0 = list(set(A0))
    while set(A) != set(A0):   # 循环直到闭包集合不再变化,得到最终的结果
        A = A0
        A0 = []
        for ch in A:
            A0 = A0 + _closure[ch]
        A0 = list(set(A0))

    return A0


def FindNewState(AB):  # 找DFA状态的单步集合
    res = dict()     # 字典,形如{'a': ['4', '1', '2', '3', '7', '6', '8'], 'b': ['5', '4', '1', '2', '7', '6']}
    for ch in Str0:
        RES = []
        for i in range(len(AB)):
            for j in range(len(Move_NFA)):
                if Move_NFA[j][0] == AB[i] and Move_NFA[j][1] == ch:
                    RES.append(Move_NFA[j][2])
        result = []
        for k in RES:
            result = result+Findclosure(k)
        res[ch] = list(set(result))
    return res


# -----------------------
with open('/compilation_principle/experiment2/data.txt', 'r') as r:
    NFA = [line.rstrip('\n') for line in r.readlines()]
print("AAAAA", NFA)
Move_NFA = NFA[2::]
for i in range(len(Move_NFA)):
    # print(Move_NFA[i])
    Move_NFA[i] = Move_NFA[i].split()  # 以空格为分隔符分开
# print(Move_NFA)
State = []
Str = []
for i in range(len(Move_NFA)):
    State.append(Move_NFA[i][0])
    State.append(Move_NFA[i][2])
    Str.append(Move_NFA[i][1])

State0 = list(set(State))    # 去重
State0.sort(key=State.index)  # 排序
Str0 = list(set(Str))
Str0.sort(key=Str.index)
if 'E' in Str0:
    Str0.remove('E')    # 字符列表去掉ε
# print(State0)
_closure = dict()    # 建立一个空字典,表示由每个状态经由条件ε可以到达的 所有状态的集合
End = NFA[1].split()
Begin = NFA[0].split()

if __name__ == '__main__':
    graph_nfaprint()

    for i in range(len(State0)):
        res = [State0[i]]
        for j in range(len(Move_NFA)):
            if Move_NFA[j][0] == State0[i] and Move_NFA[j][1] == 'E':  # 查找空闭包
                res.extend(Move_NFA[j][2])
        _closure[State0[i]]=list(set(res))
    # print(_closure )
    A = Findclosure(State0[0])
    # print(A)      # A为初始状态等价集合
    number = 0
    length = 1
    StateList = []
    StateList .append(A)
    while number < length:
        A2 = FindNewState(StateList[number])
        number = number+1
        for ch in Str0:
            temp = 1
            for p in range(length):
                if set(A2[ch]) == set(StateList[p]):
                    temp = 0
                    break
            if temp == 1:
                StateList .append(A2[ch])
                length = length+1


    Begin0 = []
    End0 = []  # 存放DFA开始状态和结束状态
    for i in range(len(Begin)):
        Begin0.append(Findclosure(Begin[i]))
    for j in range(len(End)):
        for k in range(len(StateList)):
            if End[j] in StateList[k]:
                if StateList[k] not in End0:
                    End0.append(StateList[k])

    while [] in StateList:
        StateList.remove([])   # 删除空状态,防止y 0 $的情况
    print('DFA状态表为:', StateList )
    print('DFA开始状态:', Begin0)
    print('DFA终止状态:', End0)
    graph_dfaprint(StateList, Begin0, End0)  # 画出DFA


