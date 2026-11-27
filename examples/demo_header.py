# examples/demo_header.py —— 首行参数模式的示例代码：第一行 N，第二行 N 个数，输出它们的和
import sys

def main():
    # 一次读完整个输入、按空白切词：第一行第二行怎么摆都行，只认"词"的流
    # 为什么不用 n = int(input()) 两行式读法：N=0 时没有第二行，第二次 input() 会 EOF 崩掉
    tokens = sys.stdin.read().split()
    n = int(tokens[0]) if tokens else 0          # 第一个词是参数 N（个数），后面 N 个词才是数据
    vals = list(map(int, tokens[1:1 + n]))      # 只取紧跟着的 N 个：多出来的词一律不算数
    print(sum(vals))

if __name__ == "__main__":
    main()
