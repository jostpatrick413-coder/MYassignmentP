# examples/demo_rte.py
# 故意写错的代码：用于验证测试器的 RE 判定与异常类型提取
import sys

def solve():
    data = sys.stdin.read().strip()          # 读入测试器喂来的输入
    if not data:
        return
    nums = list(map(int, data.split()))
    count = len(nums) - len(nums)            # 故意算出 0
    print(sum(nums) // count)                # 除零 → ZeroDivisionError

if __name__ == "__main__":
    solve()
