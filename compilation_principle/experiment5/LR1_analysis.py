import copy
import operator
import prettytable as pt


class SLR1(object):
    def __init__(self):
        self.grammar = []  # 原始文法集
        self.dot_grammar = []  # 加点后的文法集
        self.terminators = []
        self.temp = []
        self.first = []
        self.follow_extend = "$"
        self.vn = []  # 非终结符集合
        self.vt = []  # 终结符集合
        self.va = []  # 全部符号集合
        self.closure = []
        self.items = []
        self.search_items = []  # 加搜索符的项目规范族
        self.ACTION = []
        self.GOTO = []
        self.sentence = []
        self.symbol_stack = []
        self.shift = []
        self.delete_position = []

        self.read_data()
        self.data_processing()

    #   读取数据
    def read_data(self):
        with open("data/input.txt", 'r') as fp:
            data = [line.rstrip('\n') for line in fp.readlines()]
        with open("data/terminator.txt", 'r') as fp:
            terminators = [line.rstrip('\n') for line in fp.readlines()]

        for i in range(len(data)):
            data[i] = data[i].split()
            self.grammar.append(data[i])
        for i in range(len(terminators)):
            self.terminators += (terminators[i].split())

    #   按|划分
    def deal(self, list_ori, p):
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

    #   数据处理，提取终结符、非终结符、去除|
    def data_processing(self):
        for i in self.grammar:
            if i[0] not in self.vn:
                self.vn.append(i[0])
            for ii in i:
                if ii in self.terminators and ii not in self.vt:
                    self.vt.append(ii)
                if ii.startswith("'") and ii not in self.vt:
                    self.vt.append(ii)
        self.va = self.vn + self.vt
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

    #   寻找First集合
    def find_first(self, symbol, start):
        for sencente in self.grammar[start:]:
            if sencente[0] == symbol:
                if sencente[2] in self.terminators or sencente[2].startswith("'"):
                    if sencente[2] not in self.temp:
                        self.temp.append(sencente[2])
                else:
                    self.find_first(sencente[2], start + 1)

    #   为每个文法进行加点
    def add_point(self):
        for gram in self.grammar:
            flag = gram.index("->") - 1
            for i in range(len(gram) - flag - 1):
                temp = gram[:flag + 2 + i] + ["."] + gram[flag + 2 + i:]
                self.dot_grammar.append(temp)

    def get_vn_grammar(self, vn):
        temp = []
        for gram in self.dot_grammar:
            if gram[0] == vn and gram[2] == ".":
                temp.append(gram)
        return temp

    #   closure函数获取项目集items
    def get_closure(self, items):
        for item in items:
            if item not in self.closure:
                self.closure.append(item)
            flag = item.index(".")
            x, y = item[:flag], item[flag + 1:]
            if not y:
                continue
            symbol = y[0]
            if symbol in self.vn:
                temp = self.get_vn_grammar(symbol)
                for t in temp:
                    if t not in self.closure and t not in items:
                        self.closure.append(t)
                        items.append(t)
        return self.closure

    #   获取每个item的搜索符
    def get_search_charaster(self, itemList):
        for i in range(len(itemList)):
            if not isinstance(itemList[i][-1], list):
                itemList[i].append([])
        # print(itemList)
        for x in range(0, 2):
            for i in range(len(itemList)):
                if itemList[i][0] == "S'":  # 如果是拓广文法，则加“$“符号
                    if "$" not in itemList[i][-1]:
                        itemList[i][-1].append("$")
                else:
                    for it in itemList:
                        flag = it.index(".")
                        y = it[flag + 1:]
                        if y:
                            if y[0] == itemList[i][0]:
                                if len(y) > 2:  # "."不在item的末尾
                                    # print("y1", y, itemList[i])
                                    if y[1] in self.vt and y[1] not in itemList[i][-1]:  # 如果"."后的第二项为终结符，直接加入作为搜索符
                                        itemList[i][-1].append(y[1])
                                    if y[1] in self.vn:  # 如果"."后的第二项为非终结符，则加入first作为搜索符
                                        first = []
                                        for f in self.first:
                                            if f[0] == y[1]:
                                                first = f[1:]
                                        if chr(949) in first:
                                            first.remove(chr(949))
                                            first += y[-1][:]
                                        new = set(first).difference(set(itemList[i][-1]))
                                        # print(itemList[i][-1], y[-1], "new", list(new))
                                        if new:
                                            itemList[i][-1] += new
                                elif len(y) == 2:  # "."在item的末尾，则直接继承上一个item的搜索符
                                    # print("y2", y, itemList[i])
                                    new = set(y[-1]).difference(set(itemList[i][-1]))
                                    # print(itemList[i][-1], y[-1], "new", list(new))
                                    if new:
                                        itemList[i][-1] += new
                                else:
                                    continue
        return itemList

    #   获取所有的项目规范族
    def get_items(self):
        self.add_point()
        item = []
        item.append(self.dot_grammar[0])
        #   对I0进行初始化
        for it in item:
            vv = it[it.index('.') + 1]
            if vv in self.vn:
                temp = self.get_vn_grammar(vv)
                for t in temp:
                    if t not in item:
                        item.append(t)
        self.items.append(item[:])
        search_item = copy.deepcopy(item)
        search_item[0].append(["$"])
        self.search_items.append(self.get_search_charaster(search_item))
        #   基于I0求其他的项目规范族
        i, j = 0, 1
        for it in self.items:
            for symbol in self.va:
                new_item, subscript = self.goto(it, symbol)
                if new_item:
                    nn_item = copy.deepcopy(new_item)
                    for x in range(len(subscript)):
                        # print("self.search_items[i][subscript][-1]", self.search_items[i][subscript][-1])
                        nn_item[x].append(self.search_items[i][subscript[x]][-1])
                    tem_item = self.get_search_charaster(nn_item)
                    # print("new_item", new_item, "\ntem_item", tem_item)

                    if not self.is_inItems(tem_item):
                        self.shift.append([i, symbol, j])
                        self.items.append(new_item[:])
                        self.search_items.append(tem_item[:])
                        j += 1
                    else:
                        ind = self.search_items.index(tem_item)
                        self.shift.append([i, symbol, ind])
                    new_item.clear()
            i += 1
        self.print_cluster()

    #   构建LALR项目规范族，对相同的规范族进行搜索符的合并
    def create_LALR(self):
        same_family = []
        #   寻找所有相同的规范族
        for i in range(len(self.items)):
            j = i
            for family in self.items[i + 1:]:
                j += 1
                if self.items[i] == family:
                    same_family.append([i, j])
        self.delete_position = []

        #   对相同的item中的搜索符进行合并
        for same in same_family:
            first = same[0]
            for ind in same[1:]:
                for i in range(len(self.search_items[first])):
                    new_search = set(self.search_items[ind][i][-1]).difference(set(self.search_items[first][i][-1]))
                    self.search_items[first][i][-1] += new_search
                    if ind not in self.delete_position:
                        self.delete_position.append(ind)
                tip = 0
                for shift in self.shift:
                    for i in range(len(shift)):
                        if shift[i] == ind:
                            self.shift[tip][i] = first
                    tip += 1
        #   清除合并后相比较于之前遗留的规范族
        for i in range(len(self.search_items)):
            if i in self.delete_position:
                self.search_items[i].clear()

        self.print_cluster()
        self.construct_lr1_table()

    #   打印项目规范族
    def print_cluster(self):
        i = 0
        # print(self.search_items)
        for family in self.search_items:
            if family:
                print("I" + str(i))
                for item in family:
                    search_str = "".join(item[:-1]) + "," + str(item[-1])
                    print(search_str)
            i += 1

    #   goto函数
    def goto(self, items, symbol):
        temp = []
        new_t = []
        sub = []
        i = 0
        for it in items:
            flag = it.index(".")
            x, y = it[:flag], it[flag + 1:]
            if y:
                if y[0] == symbol:
                    new_t.clear()
                    new_t = x + [y[0]] + ["."] + y[1:]
                    temp.append(new_t[:])
                    sub.append(i)
            i += 1
        if temp:
            new_item = self.get_closure(temp)
            return new_item, sub
        return False, False

    #   判断当前的item是否已经存在在items中
    def is_inItems(self, item):
        if not item:
            return False
        num = 0
        for it in self.search_items:
            if operator.eq(it, item):
                return num
            num += 1
        return False

    #   构建分析表
    def construct_lr1_table(self):
        self.init_table()
        for status in self.shift:
            if self.shift.index(status) == 0:  # 判断是否是接受态
                self.ACTION[status[2]][len(self.vt) - 1] = "ACC"
            if status[1] in self.vt:  # 构建ACTION表中的移进状态，即"s"状态
                j = self.vt.index(status[1])
                self.ACTION[status[0]][j] = "s" + str(status[2])
            else:  # 构建GOTO表中的状态
                j = self.vn.index(status[1])
                self.GOTO[status[0]][j] = status[2]
        for i in range(len(self.search_items)):  # 构建ACTION表中的规约状态，即“r”状态
            for j in range(len(self.vt)):
                if self.ACTION[i][j] != " ":
                    continue
                else:
                    if self.search_items[i]:
                        for search in self.search_items[i][0][-1]:
                            if search == self.vt[j]:
                                if self.items[i][0].index(".") != len(self.items[i][0]) - 1:
                                    continue
                                o_item = copy.deepcopy(self.items[i][0][:-1])
                                ind = self.grammar.index(o_item)
                                self.ACTION[i][j] = "r" + str(ind)
        self.print_lr1_table()

    #   初始化分析表
    def init_table(self):
        self.ACTION.clear()
        self.GOTO.clear()
        for i in range(len(self.items)):
            self.ACTION.append([])
            self.GOTO.append([])
            for x in range(len(self.vt)):
                self.ACTION[i].append(" ")
            for y in range(len(self.vn)):
                self.GOTO[i].append(" ")

    def predict_analyzer(self):
        stack = []
        # self.sentence = ["'id'", "*", "'id'", "+", "'id'"]
        self.sentence = ["b", "b", "a"]
        print('\n----分析过程----')
        print('%-30s' % 'Stack', end='')
        print('%-30s' % 'Input', end='')
        print('Action')

        self.sentence.append("$")
        stack.append(0)
        is_reduce = False
        find = ""
        ss = (" ".join(str(x) for x in stack))
        se = (" ".join(str(x) for x in self.sentence))
        print('%-30s' % ss, '%-30s' % se, "   ")
        while True:
            if not is_reduce:
                symbol = self.sentence.pop(0)
            find = self.ACTION[stack[-1]][self.vt.index(symbol)]

            if find[0] == 's':
                is_reduce = False
                stack.append(symbol)
                stack.append(int(find[1]))

                ss = (" ".join(str(x) for x in stack))
                se = (" ".join(str(x) for x in self.sentence))
                print('%-30s' % ss, '%-30s' % se, "移进")

            elif find[0] == 'r':
                is_reduce = True
                num = int(find[1])
                g = self.grammar[num]
                right_num = 2 * (len(g) - 2)
                for i in range(right_num):
                    stack.pop()
                find = self.GOTO[stack[-1]][self.vn.index(g[0])]
                stack.append(g[0])

                gg = (" ".join(str(x) for x in g))
                ss = (" ".join(str(x) for x in stack))
                se = (" ".join(str(x) for x in self.sentence))
                print('%-30s' % ss, '%-30s' % se, "按 %s 归约" % (gg))

                if find:
                    stack.append(find)
                else:
                    print("ERROR!")
                    return False
            elif find == "ACC":
                print("Accept!")
                return True
            else:
                print("ERROR!")
                return False

    #  打印分析表

    #   打印分析表
    def print_lr1_table(self):
        print('\n----LR1分析表----')
        tb = pt.PrettyTable()
        num = []
        for i in range(len(self.ACTION)):
            num.append(i)
        tb.add_column("状态", num)
        for i in range(len(self.vt)):
            actiom_column = []
            for j in range(len(self.ACTION)):
                actiom_column.append(self.ACTION[j][i])
            tb.add_column(self.vt[i], actiom_column)

        for i in range(len(self.vn)):
            goto_column = []
            for j in range(len(self.GOTO)):
                goto_column.append(self.GOTO[j][i])
            tb.add_column(self.vn[i], goto_column)

        flag = 0
        for i in self.delete_position:
            tb.del_row(i - flag)
            flag += 1

        print(tb, "\n")


if __name__ == '__main__':
    SLR = SLR1()
    print(SLR.vn, SLR.grammar)
    for vn in SLR.vn:
        SLR.temp.clear()
        SLR.temp.append(vn)
        SLR.find_first(vn, 0)
        SLR.first.append(SLR.temp[:])
    print(SLR.first)

    SLR.get_items()
    SLR.vn.pop(0)

    SLR.vt = list(set(SLR.vt))
    SLR.vt.append("$")
    SLR.construct_lr1_table()
    # SLR.predict_analyzer()
    SLR.create_LALR()
