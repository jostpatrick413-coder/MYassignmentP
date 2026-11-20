import random

class DataGenerator:
    def __init__(self, min_val=1, max_val=100, seed=None):
        self.min_val = min_val
        self.max_val = max_val
        if seed is not None:   # 给了种子就固定"随机"序列；不给则每次交给系统，各不相同
            random.seed(seed)

    def generate_array(self, n):
        # 生成一个长度为 n 的随机整数数组
        return [random.randint(self.min_val, self.max_val) for _ in range(n)]

    def generate_edge_cases(self,n):
        # 生成极端的边界情况
        return {
            "all_same": [self.min_val] * n,               # 比如全是 1
            "already_sorted": list(range(1, n + 1)),      # 1 到 n 升序，共 n 个数
            "reverse_sorted": list(range(n, 0, -1)),      # 10 到 1 降序
            "extreme_values": [self.min_val if i % 2 == 0 else self.max_val for i in range(n)],  # 极值交替，共 n 个
            "empty": [],                                  # 空数组：len=0，除法/取模题第一崩溃点
            "single": [self.max_val],                     # 单元素：下标越界高发场景
            "all_zero": [0] * n,                          # 全 0：求和/除法翻车点
            "zero_alt": [0 if i % 2 == 0 else self.max_val for i in range(n)],  # 0 与极值交替，比全 0 更隐蔽
            "neg_pos_alt": [-self.max_val if i % 2 == 0 else self.max_val for i in range(n)],  # 负正交替：符号试金石
        }
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