import operator
import prettytable as pt


#   构建自下而上的语法分析类
class LR1(object):
    def __init__(self):
        self.grammar = []
        self.dot_grammar = []
        self.terminators = []
        self.vn = []    #   非终结符
        self.vt = []    #   终结符
        self.va = []    #   所有的文法符号
        self.closure = []
        self.items = []
        self.ACTION = []    #   ACTION表
        self.GOTO = []    #    GOTO表
        self.sentence = []
        self.ll = 0
        self.symbol_stack = []

    #   读入数据
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

    #   划分数据
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

    #   对数据进行处理
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

    #   对每个项目进行加点操作
    def add_point(self):
        for gram in self.grammar:
            flag = gram.index("->") - 1
            for i in range(len(gram) - flag - 1):
                temp = gram[:flag+2+i] + ["."] + gram[flag+2+i:]
                self.dot_grammar.append(temp)

    #   获取closure函数
    def get_closure(self, items):
        for item in items:
            if item not in self.closure:
                self.closure.append(item)
            flag = item.index(".")
            x, y = item[:flag], item[flag+1:]
            if not y:
                continue
            symbol = y[0]
            if symbol in self.vn:
                temp = self.get_vn_grammar(symbol)
                for t in temp:
                    if t not in self.closure:
                        self.closure.append(t)
        return self.closure

    #   获取闭包
    def get_vn_grammar(self, vn):
        temp = []
        for gram in self.dot_grammar:
            if gram[0] == vn and gram[2] == ".":
                temp.append(gram)
        return temp

    #   构建项目规范族
    def get_items(self):
        self.add_point()
        item = []
        item.append(self.dot_grammar[0])
        for it in item:
            vv = it[it.index('.')+1]
            if vv in self.vn:
                temp = self.get_vn_grammar(vv)
                for t in temp:
                    if t not in item:
                        item.append(t)
        self.items.append(item[:])
        for it in self.items:
            for symbol in self.va:
                new_item = self.goto(it, symbol)

                if new_item:
                    if not self.is_inItems(new_item):
                        self.items.append(new_item[:])
                    new_item.clear()
        self.item_tidy()

    #   goto函数构造
    def goto(self, items, symbol):
        temp = []
        new_t = []
        for it in items:
            flag = it.index(".")
            x, y = it[:flag], it[flag+1:]
            if y:
                if y[0] == symbol:
                    new_t.clear()
                    new_t = x + [y[0]] + ["."] + y[1:]
                    temp.append(new_t[:])
        if temp:
            new_item = self.get_closure(temp)
            return new_item
        return False

    #   判断当前项目是否在项目规范族中
    def is_inItems(self, item):
        if not item:
            return False
        num = 0
        for it in self.items:
            if operator.eq(it, item):
                return num
            num += 1
        return False

    #   整理规范族
    def item_tidy(self):
        flag = []
        for i in range(len(self.items)):
            for j in range(0, i):
                if operator.eq(self.items[i][0], self.items[j][0]):
                    flag.append(i)
                    continue
            for it in self.items[i]:
                if it.index('.')+1 == len(it):
                    continue
                vv = it[it.index('.') + 1]
                if vv in self.vn:
                    temp = self.get_vn_grammar(vv)
                    if temp:
                        for t in temp:
                            if t not in self.items[i]:
                                self.items[i].append(t)
        for i in flag:
            del self.items[i]

    #   构建分析表
    def construct_lr_table(self):
        self.vn.pop(0)
        self.init_table()
        self.lr_is_legal()
        extended_grammar = self.grammar[0]
        i, j = 0, 0
        for item in self.items:
            for it in item:
                flag = it.index(".")
                x, y = it[:flag], it[flag + 1:]
                # print("\n", i, x, y, " ", it)
                if not y:
                    if operator.eq(x, extended_grammar):
                        self.ACTION[i][len(self.vt)-1] = "ACC"
                    ind = self.grammar.index(x)
                    # print(ind)
                    if ind:
                        for k in range(len(self.ACTION[i])):
                            self.ACTION[i][k] = "r" + str(ind)
                    # print("ny", ind, self.ACTION[i])
                else:
                    next_item = self.goto(item, y[0])
                    # print("goto", next_item)
                    flag = self.is_inItemsS(next_item)
                    next_item.clear()
                    if flag:
                        if y[0] in self.vt:
                            j = self.vt.index(y[0])
                            self.ACTION[i][j] = "s" + str(flag)
                        if y[0] in self.vn:
                            j = self.vn.index(y[0])
                            self.GOTO[i][j] = flag
                    # print("y", flag, self.ACTION[i], self.GOTO[i])
            i += 1

    #   寻找DFA关系
    def is_inItemsS(self, item):
        if not item:
            return False
        num = 0
        remember = self.get_closure(item)
        for it in self.items:
            if operator.eq(it, remember):
                return num
            num += 1
        return False

    #   获取规约式
    def find_closure(self, it):
        flag = it.index(".")
        x, y = it[:flag], it[flag + 1:]
        mgram = x + y
        try:
            position = self.grammar.index(mgram)
            return position
        except ValueError:
            return False

    #   初始化分析表
    def init_table(self):
        for i in range(len(self.items)):
            self.ACTION.append([])
            self.GOTO.append([])
            for x in range(len(self.vt)):
                self.ACTION[i].append(" ")
            for y in range(len(self.vn)):
                self.GOTO[i].append(" ")

    #   判断当前的动作是否合法
    def lr_is_legal(self):
        protocol_flag = 0
        shift_flag = 0
        for item in self.items:
            for it in item:
                flag = it.index(".")
                x, y = it[:flag], it[flag + 1:]
                if not y:
                    if protocol_flag != 0 or shift_flag != 0:
                        return False
                    protocol_flag = 1
                else:
                    if y[0] in self.vt:
                        shift_flag = 1
        return True

    #   构建分析过程
    def predict_analyzer(self):
        stack = []
        # self.sentence = ["'id'", "*", "'id'", "+", "'id'"]
        self.sentence = ["(", "a", ",", "a",")"]
        print('\n----分析过程----')
        print('%-30s' % 'Stack', end='')
        print('%-30s' % 'Input', end='')
        print('Action')

        self.sentence.append("$")
        stack.append(0)
        is_reduce = False
        find = ""
        while True:
            if not is_reduce:
                symbol = self.sentence.pop(0)
            find = self.ACTION[stack[-1]][self.vt.index(symbol)]

            if find[0] == 's':
                is_reduce = False
                stack.append(symbol)
                stack.append(int(find[1]))

                ss = (" ".join(str(x) for x in stack))
                se = (" ".join(str(x) for x in [symbol] + self.sentence))
                print('%-30s' %ss, '%-30s' %se, "移进")

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
                se = (" ".join(str(x) for x in [symbol] + self.sentence))
                print('%-30s' %ss, '%-30s' %se, "按 %s 归约" % (gg))

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

    #   打印分析表
    def print_lr_table(self):
        print('\n----LR分析表----')
        print('%-8s|' % ' ', end='')
        print('%-23s|' % 'ACTION', end='')
        print('%-10s\n' % 'GOTO', end='')
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
        print(tb)


if __name__ == '__main__':
    # predict_string = input()
    LR_analysis = LR1()
    LR_analysis.read_data()
    LR_analysis.data_processing()
    print(LR_analysis.grammar)
    print(LR_analysis.vt, LR_analysis.vn)
    LR_analysis.add_point()

    LR_analysis.get_items()
    for i in range(len(LR_analysis.items)):
        print(i, LR_analysis.items[i])

    LR_analysis.vt.append("$")
    LR_analysis.construct_lr_table()

    LR_analysis.print_lr_table()

    LR_analysis.predict_analyzer()