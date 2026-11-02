# examples/demo_solution.py
# 模拟"你要交到 OJ 的代码"：读入一行整数，输出它们的平均值（整除）
import sys

def solve():
    data = sys.stdin.read().strip()          # 读入测试器喂来的全部输入，去掉首尾空白
    if not data:                             # 防御：没有输入就什么都不做
        return
    nums = list(map(int, data.split()))      # 按空格拆成字符串，再逐个转成整数列表
    avg = sum(nums) // len(nums)             # 求和除以个数，// 是整除（不产生小数）
    print(avg)                               # 打印结果，测试器会捕获这一行

if __name__ == "__main__":
    solve()
##简单的代码模拟器。qoder告诉我最后两行可以防止被误用，只能用于跑py