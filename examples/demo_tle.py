# examples/demo_tle.py
# 故意死循环的代码：用于验证测试器的 TLE 判定
import sys

def solve():
    data = sys.stdin.read()
    if not data:
        return
    x = 0
    while True:        # 故意死循环，永远出不去
        x += 1

if __name__ == "__main__":
    solve()
