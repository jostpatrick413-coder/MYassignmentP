# examples/demo_wa.py
# 模拟"交到 OJ 就 WA 的坏代码"：求平均值时分母手滑写成了 n-1
# 在 OJ 上它不会报错、只会默默 WA；本地对拍第一组就能把它揪出来
import sys

def solve():
    data = sys.stdin.read().strip()          # 读入测试器喂来的全部输入，去掉首尾空白
    if not data:                             # 防御：没有输入就什么都不做
        return
    nums = list(map(int, data.split()))      # 按空格拆成字符串，再逐个转成整数列表
    avg = sum(nums) // (len(nums) - 1)       # 错误：分母应为 len(nums)，这里故意少 1
    print(avg)                               # 打印结果，测试器会捕获这一行

if __name__ == "__main__":
    solve()
#与 demo_solution 对照：全篇只差一个 "-1"，OJ 上这就是一次找不到原因的 WA
