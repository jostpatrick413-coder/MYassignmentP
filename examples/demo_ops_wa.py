# examples/demo_ops_wa.py
# 故意写错的"运算符统计"：只数了 +，漏掉 - * / ——对拍应能抓出 WA
import sys

def solve():
    data = sys.stdin.read().strip()
    if not data:
        return
    tokens = data.split()
    print(tokens.count("+"))            # 错在这：只统计 + 一种

if __name__ == "__main__":
    solve()
