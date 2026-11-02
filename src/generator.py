import random

class DataGenerator:
    def __init__(self, min_val=1, max_val=100):
        self.min_val = min_val
        self.max_val = max_val

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