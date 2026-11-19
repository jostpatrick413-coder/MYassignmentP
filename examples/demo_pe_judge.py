# examples/demo_pe_judge.py
# demo_pe.py 的裁判：同一道题的正确输出格式——平均值、元素个数各占一行
# 数值与 demo_pe 完全一致，唯一区别是空白摆法（正好演示 PE 与 WA 的分界线）
import sys

def solve():
    data = sys.stdin.read().strip()          # 读入测试器喂来的全部输入，去掉首尾空白
    if not data:                             # 防御：没有输入就什么都不做
        return
    nums = list(map(int, data.split()))      # 按空格拆成字符串，再逐个转成整数列表
    avg = sum(nums) // len(nums)             # 平均值（整除）
    print(avg)                               # 按题意：第一个数单独一行
    print(len(nums))                         # 按题意：第二个数单独一行

if __name__ == "__main__":
    solve()
# ==== 学习笔记（本轮新增，精简版）====
# 【裁判的格式权威】裁判不但数值要对，格式也要按题意来——它就是"标准答案的摆法"。
#   对拍时它输出的 "46\n5" 是期望格式；待测摆成 "46 5" 就判 PE（数值没错、格式错）。
