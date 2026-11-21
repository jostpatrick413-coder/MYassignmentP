# examples/demo_ops.py
# 模拟"运算符统计"题：读入空格分隔的符号串，统计其中运算符（+ - * /）的个数
import sys

def solve():
    data = sys.stdin.read().strip()     # 读入全部输入，去掉首尾空白
    if not data:                        # 防御：没有输入就什么都不做
        return
    tokens = data.split()               # 按空白切成一个个符号
    count = sum(1 for t in tokens if t in "+-*/")   # 统计四个运算符出现几次
    print(count)

if __name__ == "__main__":
    solve()
