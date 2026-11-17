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
            "extreme_values": [self.min_val if i % 2 == 0 else self.max_val for i in range(n)]  # 极值交替，共 n 个
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