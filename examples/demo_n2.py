# examples/demo_n2.py
# 故意写成 O(N^2) 的代码：用于验证复杂度分析器
import sys

def solve():
    data = sys.stdin.read().strip()
    if not data:
        return
    a = list(map(int, data.split()))
    s = 0
    for x in a:              # 外层跑 N 次
        for y in a:          # 内层也跑 N 次 → 总共约 N^2 次
            s += (x + y) % 7
    print(s % 1000)

if __name__ == "__main__":
    solve()
