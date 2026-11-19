# examples/demo_pe.py
# 模拟"数值全对、格式不对"的坏代码：题目要求输出两个数、一行一个，它却用空格拼成一行
# 在 OJ 上这就是 PE（格式错误）；对拍归一化后能认出"数值没错，只差摆法"
import sys

def solve():
    data = sys.stdin.read().strip()          # 读入测试器喂来的全部输入，去掉首尾空白
    if not data:                             # 防御：没有输入就什么都不做
        return
    nums = list(map(int, data.split()))      # 按空格拆成字符串，再逐个转成整数列表
    avg = sum(nums) // len(nums)             # 平均值（整除）
    print(avg, len(nums))                    # 格式错误：题意应一行一个数，这里拼成一行

if __name__ == "__main__":
    solve()
# ==== 学习笔记（本轮新增，精简版）====
# 【PE 演示】与 demo_pe_judge 对照：两边数值完全一样（平均值、元素个数），唯一区别是
#   demo_pe 输出 "46 5"（一行），judge 输出 "46\n5"（一行一个）——这就是格式错误的模样。
#   对拍逐字比对会抓它，归一化比对能认出"数值没错、只差空白"。
