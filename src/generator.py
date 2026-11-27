import random

class DataGenerator:
    def __init__(self, min_val=1, max_val=100, seed=None, rows=1, cols=10, alphabet=None, header=False):
        self.min_val = min_val
        self.max_val = max_val
        self.rows = rows   # 行数旋钮：int = 固定；tuple(小,大) = 每个用例掷一次
        self.cols = cols   # 每行输入数旋钮：int = 每行一样多；tuple = 每行各自掷（不定行）
        self.alphabet = alphabet or None   # 符号模式开关：给了字符集合就掷符号；None（或空串）= 照旧掷整数
        self.header = header   # 形状模板开关：True = 首行参数（第一行 N + N 个值），矩形旋钮换语义
        if seed is not None:   # 给了种子就固定"随机"序列；不给则每次交给系统，各不相同
            random.seed(seed)

    def _roll(self, spec):
        # 旋钮取值：int 原样返回；tuple 在范围内掷一次骰子（掷骰子同样走 random 流，受 seed 管）
        if isinstance(spec, tuple):
            return random.randint(spec[0], spec[1])
        return spec

    def _roll_value(self):
        # 掷一个"值"：全项目唯一的出数口。符号模式从字符集合随机挑一个（random.choice），
        # 整数模式在 min~max 里掷（randint）——两种模式共用一个出水口，下游全不用改。
        if self.alphabet is not None:
            return random.choice(self.alphabet)
        return random.randint(self.min_val, self.max_val)

    def generate_array(self, n):
        # 生成一个长度为 n 的随机整数数组
        # （符号模式下掷的是 alphabet 里的字符；本函数同时供对拍与复杂度分析用，同样吃这个旋钮）
        return [self._roll_value() for _ in range(n)]

    def generate_grid(self, rows):
        # 造 rows 行的矩阵：cols 固定则每行一样多；cols 是范围则每行各自掷（参差不齐的不定行）
        if isinstance(self.cols, tuple):
            return [self.generate_array(self._roll(self.cols)) for _ in range(rows)]
        return [self.generate_array(self.cols) for _ in range(rows)]

    def generate_random_case(self):
        # 随机用例：行数掷一次，行内个数按 cols 旋钮逐行掷
        return self.make_case("random_case")

    def _reshape(self, vals, cols):
        # 把一维模式切回 rows×cols 矩阵；cols=0（行里不装数）时直接给空矩阵，避免切出死循环
        if cols == 0:
            return []
        return [vals[i:i + cols] for i in range(0, len(vals), cols)]

    def make_case(self, name):
        # 按名造一个用例（重造机制每次调用它重新掷形状与数值）
        if self.header:                                 # 首行参数模板：形状换成"第一行 N + N 个值"，旋钮语义见 _make_header_case
            return self._make_header_case(name)
        if name == "empty":                              # 0 行：空输入，形状本身就是边界
            return []
        if name == "single":                             # 1 行 1 个：下标越界高发场景
            return [[self.alphabet[-1] if self.alphabet else self.max_val]]   # 符号模式取集合末字符（类比整数版取极值）
        if name == "random_case":                        # 随机用例：行数掷一次，行内个数逐行掷
            return self.generate_grid(self._roll(self.rows))
        rows, cols = self._roll(self.rows), self._roll(self.cols)   # 值模式用例：掷一次形状，规整矩形
        total = rows * cols
        if self.alphabet is not None:
            flat = self._symbol_pattern(name, total)     # 符号模式：形态从字符集合取材
        else:
            flat = {
                "all_same": [self.min_val] * total,               # 比如全是 1
                "already_sorted": list(range(1, total + 1)),      # 1 到 total 升序
                "reverse_sorted": list(range(total, 0, -1)),      # total 到 1 降序
                "extreme_values": [self.min_val if i % 2 == 0 else self.max_val for i in range(total)],  # 极值交替
                "all_zero": [0] * total,                          # 全 0：求和/除法翻车点
                "zero_alt": [0 if i % 2 == 0 else self.max_val for i in range(total)],  # 0 与极值交替，比全 0 更隐蔽
                "neg_pos_alt": [-self.max_val if i % 2 == 0 else self.max_val for i in range(total)],  # 负正交替：符号试金石
            }[name]
        return self._reshape(flat, cols)

    def _make_header_case(self, name):
        # 首行参数模板：第一行 = 参数 N（"个数"是元数据，永远是整数），第二行 = N 个值
        # 旋钮换语义：--n 从"每行输入数"变成"参数 N"（int=固定、范围=每次掷）；--rows 本模板用不上，自然失效
        if name == "empty":                              # N=0：只有参数行，后面没有数据
            return [[0]]
        if name == "single":                             # N=1 配一个值：参数最小、数据最少（值取极值/末字符）
            return [[1], [self.alphabet[-1] if self.alphabet else self.max_val]]
        n = self._roll(self.cols)
        if n == 0:
            return [[0]]                                 # --n 0：同样只有参数行（与 empty 同构）
        if name == "random_case":                        # 随机用例：N 掷一次，后面 N 个随机值
            return [[n], self.generate_array(n)]
        if self.alphabet is not None:
            flat = self._symbol_pattern(name, n)         # 符号模式：数据行从字符集合取材（N 行仍是整数）
        else:
            flat = {
                "all_same": [self.min_val] * n,
                "already_sorted": list(range(1, n + 1)),
                "reverse_sorted": list(range(n, 0, -1)),
                "extreme_values": [self.min_val if i % 2 == 0 else self.max_val for i in range(n)],
                "all_zero": [0] * n,
                "zero_alt": [0 if i % 2 == 0 else self.max_val for i in range(n)],
                "neg_pos_alt": [-self.max_val if i % 2 == 0 else self.max_val for i in range(n)],
            }[name]
        return [[n], flat]

    def _symbol_pattern(self, name, total):
        # 符号模式的边界形态：整数版的"升降序/极值"没有符号对应物，换成对字符集合的覆盖方式
        a = self.alphabet
        if name == "all_same":
            return [a[0]] * total                              # 全同：全是集合第一个符号
        if name == "cycle":
            return [a[i % len(a)] for i in range(total)]       # 顺循环：整个集合铺满（类比"全值域顺序覆盖"）
        if name == "reverse_cycle":
            return [a[-(i % len(a)) - 1] for i in range(total)]  # 逆循环：反向铺满
        if name == "alt_two":
            return [a[0] if i % 2 == 0 else a[-1] for i in range(total)]  # 首尾两符号交替（类比极值交替）
        return [a[0]] * total   # 未知名字不该出现（generate_edge_cases 控制键名）；兜底给全同

    def generate_edge_cases(self):
        # 生成极端的边界情况
        names = (["all_same", "cycle", "reverse_cycle", "alt_two", "empty", "single"]
                 if self.alphabet is not None else
                 ["all_same", "already_sorted", "reverse_sorted", "extreme_values",
                  "empty", "single", "all_zero", "zero_alt", "neg_pos_alt"])
        return {name: self.make_case(name) for name in names}
#randint（a，b）为a<=x<=b的随机整数生成器
#class创建了一个类，函数的相关初始值为min=1，max=100
#边界函数为全等，正逆序，边界案例等。
###主要用于一行整数型的数据
# ==== 学习笔记（本轮新增内容，精简版）====
# 【伪随机】计算机没有真随机：random.randint 背后是固定公式（梅森旋转），靠内部状态
#   一步步"发牌"。整串数字完全由起始状态决定——这个起始状态就是种子（seed）。
# 【random.seed(42)】把发牌机重置到"42 号开局"，之后发的牌一模一样；同 seed 必同序列。
# 【if seed is not None】为什么不用 if seed：seed=0 是合法种子但 0 是"假"，会被误判成没给——
#   经典陷阱。is not None 只认"真的没给"这一种情况。
# 【默认 None】不给种子时 Python 拿系统熵（时间等）自动挑开局 → 每次不同，测试才有变化；
#   给了种子 → 每次相同，抓到的 WA 才能复现。两种需求、一个参数。
# 【随机只在生成器里】随机数只从 DataGenerator 出生，seed 就该长在它身上；
#   runner 只负责跑代码，不造数据，不该管种子。
# ==== 学习笔记（边界补全本轮新增，精简版）====
# 【边界三维度】排列形态（全同/升降序/交替）之外，还有两个更致命的维度：
#   规模边界（空数组/单元素：len 相关代码的崩溃点）与值域边界（0/负数：除法与符号的翻车点）。
#   随机数据范围 1~100 永远造不出这两类——坏代码在"看起来正常"的数据下安然无恙，
#   边界用例的价值就是逼它现形。
# 【空数组 ≠ 空字符串】[] 是"长度为 0 的列表"，拼成输入串后是 ""；子进程读到空 stdin。
#   没写防御的代码（sum//len）当场 ZeroDivisionError——这正是要抓给用户看的。
# 【单元素】只跑一轮的循环最容易暴露下标越界（比如访问 arr[1]）；single 顺手用 max_val 测极值。
# 【确定性】新边界全是固定模式、不吃随机数：与 --seed 无关，任何环境跑出来的输入都一样。
# ==== 学习笔记（矩形模型本轮新增，精简版）====
# 【三个旋钮】输入结构不写"格式描述语言"，只留三个旋钮：行数、每行输入数、取值范围（--min/--max）。
#   约定优于配置：大部分题目输入就是"一堆数摆成若干行"，矩形覆盖绝大多数场景；
#   首行参数（"第一行 N，接着 N 个数"）等复杂结构留了口子，后置。
# 【旋钮的两种取值】int = 固定值；tuple(小,大) = 每次掷骰子。同一个参数、两种形态，
#   "定行/不定行"不再是两套机制——只是同一个旋钮给值还是给范围。
# 【isinstance 分流】_roll 用 isinstance(spec, tuple) 区分"固定/范围"：tuple 就 randint，int 就原样返回。
#   为什么不用 type()==tuple：isinstance 认子类，习惯上更稳。
# 【每行各自掷 vs 掷一次】cols 是范围时 random_case 每行各掷一次（参差不齐，这才叫"不定行"）；
#   边界用例掷一次再整块重塑（值模式要规整矩形才好手算核对）。
# 【0 行 = 空输入】rows 范围含 0（如 0-3）时 random_case 可能掷出空输入——不定行的自然产物，
#   而不是专门构造的边界用例。
# 【_reshape 守卫】cols=0 时"每行装 0 个数"，range(0, total, 0) 会 ValueError，先判掉返回 []。
# 【掷骰子受 seed 管】范围掷骰子走的也是 random 流：同 seed 连跑两次，连"掷出来的行数列数"都一样。
# ==== 学习笔记（符号输入轮本轮新增，精简版）====
# 【符号 = 值维度升级】用户最初的判断成立：符号输入不是新结构，是"取值范围"旋钮的升级——
#   整数模式掷 randint(min,max)，符号模式掷 random.choice(alphabet)。行数/每行个数照旧。
# 【唯一出水口 _roll_value】generate_array 是下游所有数据的源头（边界/随机/对拍/复杂度分析都过它），
#   把"掷一个值"收拢成 _roll_value 一个函数：加符号模式只改这一处，下游一行不动——收口的价值。
# 【符号版边界 = 覆盖方式】整数版的升降序/极值没有符号对应物，换成对字符集合的覆盖：
#   全同（all_same）、顺/逆循环铺满（cycle/reverse_cycle）、首尾交替（alt_two）+ 规模边界（empty/single）。
# 【单元素取末字符】single 类比整数版"取极值"：符号版取集合末字符，两个模式同一套设计语言。
# 【alphabet or None】空字符串 "" 是"假"：--alphabet "" 会被当成没给、退回整数模式——防止空集合让 choice 崩掉。
# ==== 学习笔记（首行参数轮本轮新增，精简版）====
# 【形状模板】矩形是"形状旋钮 + 值旋钮"；首行参数是另一个形状模板——不是新机制，只是把同一套旋钮
#   换一套摆放规则：--n 从"每行输入数"变成"参数 N"，值旋钮（--min/--max/--alphabet）照旧管数据行。
#   make_case 开头一行 if self.header 分流，下游（拼串/runner/对拍）一行不改——模板内部的事不外泄。
# 【N 是元数据不是数据】参数 N 永远是整数（它是"个数"，是结构信息）；符号模式只影响数据行的值。
#   所以符号+header 组合下第一行仍是数字、第二行才是符号——两种旋钮的职责清清楚楚。
# 【empty 在 header 下的对应物】矩形里"空输入"= 0 行；header 里最接近的边界 = N=0（只有参数行，
#   后面没有数据）。[[0]] 拼出来是 "0"——待测代码读到 N=0 就该什么都不做，防御差的当场崩。
# 【single = N=1】参数最小配数据最少，值顺手取极值（整数版 max_val / 符号版末字符），
#   与矩形版 single 同一设计语言：规模边界 × 值域边界双押。
# 【--rows 自然失效】两行结构没有"行数"可言：header 模式根本不看 self.rows。
#   这是约定优于配置的代价——一个旋钮管一个模板，模板换了，管不着的旋钮就安静失效。# 【执行路径追踪】--header --n 5 下 already_sorted 组的完整路径：
#   main:82 generate_edge_cases → generator:48 make_case → :50 if self.header（唯一分水岭）
#   → _make_header_case → :80 n=_roll(cols)=5 → :85-93 flat=[1..5] → :94 return [[5],[1..5]]
#   → main:86 join 成 "5\n1 2 3 4 5"（拼串代码矩形轮写的，一字未改）→ runner 喂子进程。
#   分叉：empty 在 :77 直接 return [[0]]（掷 N/造值全不执行）；single 在 :79 return [[1],[极值]]。
