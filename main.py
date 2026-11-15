# main.py —— OJ 本地样例测试器 v1.2 的入口
import argparse
from src.generator import DataGenerator
from src.runner import CodeRunner
from src.analyzer import ComplexityAnalyzer
from src.checker import Comparator

SCALES = [300, 1000, 2000]   # 复杂度分析的三档规模（小/中/大）

def main():
    # argparse 四步：造"菜单簿" → 登记规则 → 解析 → 取值
    parser = argparse.ArgumentParser(description="OJ 本地样例测试器：生成数据、跑代码、判 RE/TLE/WA")
    # 每组测试数据的规模，以后想测更大的数，改这里就行
    parser.add_argument("--n", type=int, default=10, help="每组测试数据的规模")
    # 跑完 5 组用例后，是否追加复杂度分析
    parser.add_argument("--analyze", action="store_true", default=True, help="追加复杂度分析（默认开启）")
    parser.add_argument("--no-analyze", dest="analyze", action="store_false", help="跳过复杂度分析")
    parser.add_argument("--code", default="examples/demo_solution.py", help="待测代码路径")
    parser.add_argument("--min", type=int, default=1, help="随机数据最小值")
    parser.add_argument("--max", type=int, default=100, help="随机数据最大值")
    parser.add_argument("--timeout", type=float, default=2.0, help="单组超时阈值（秒）")
    parser.add_argument("--check", action="store_true", help="开启对拍模式（WA 检测）")
    parser.add_argument("--brute", default=None, help="对拍裁判（暴力解）路径，缺省用 demo_solution")
    args = parser.parse_args()   # 解析：命令行原始字符串对照规则，结果装进 args 托盘

    print("=== OJ 本地样例测试器 (v1.2) ===")
    print()

    generator = DataGenerator(min_val=args.min, max_val=args.max)   # 数据范围来自命令行
    runner = CodeRunner(args.code, timeout=args.timeout)            # 待测代码与超时都来自命令行

    if args.check:
        brute_path = args.brute if args.brute else "examples/demo_solution.py"
        Comparator(generator, rounds=20, small_n=5, timeout=args.timeout).check(args.code, brute_path)
        return

    test_cases = generator.generate_edge_cases(args.n)       # 4 组边界用例
    test_cases["random_case"] = generator.generate_array(args.n)  # 再加 1 组随机用例

    for name, arr in test_cases.items():                # 逐个用例测试
        input_str = " ".join(map(str, arr))             # 把列表拼成 "3 1 4 ..." 形式的字符串
        print(f"--- 正在测试: {name} ---")
        print(f"输入数据: {input_str}")

        status, elapsed, output = runner.run_test(input_str)  # 核心：调用你的 runner

        if status == "Finished":
            print(f"[通过] 耗时: {elapsed:.4f}s")
            print(f"程序输出: {output}")
        elif status.startswith("RE"):
            error_name = status.split("(", 1)[1].rstrip(")")  # 括号里是具体异常类型
            print(f"[运行时错误] {error_name}  耗时: {elapsed:.4f}s")
            print(f"报错信息: {output}")
        elif status == "TLE (Time Limit Exceeded)":
            print(f"[超时 TLE] 判定时间: {elapsed:.1f}s")
        print()

    if args.analyze:
        analyzer = ComplexityAnalyzer(generator, runner)  # 分析器复用同一个生成器与运行器
        analyzer.analyze(SCALES)

if __name__ == "__main__":
    main()
#我将花费一个学期理解这个代码。这个import让我认识到库是一个py可调用的代码群，所以我可以自己写一些库参与项目。
#然后是这种文件间的配合很有工程之美，从DG和CR里分别造数据和启动待测代码并接住返回的数据。
# ==== 学习笔记（本轮新增内容，精简版）====
# 【argparse 四步】import → ArgumentParser() 造"菜单簿" → add_argument() 往菜单登记 → parse_args() 解析。
# 【声明 ≠ 变量】add_argument 不是定义变量，是登记规则；parse_args 拿 sys.argv[1:] 的原始字符串
#   对照规则逐条匹配、转类型、填默认值，结果装进 args"托盘"（Namespace 对象）。
# 【-- 的意义】约定：以 -- 开头的是"选项名"不是数据；登记 --n 时自动剥掉 --，结果存进 args.n。
# 【action】store=吃后面一个值（默认）；store_true=不吃值、出现即真；store_false=出现即假。
# 【dest="analyze"】强制指定目标盒子：--analyze 与 --no-analyze 两个门、同一个房间 args.analyze。
# 【type=int】命令行里一切皆字符串，type 负责转换并校验（-n abc 会自动报错退出）。
# 【--help 白送】打印全部登记项与说明后退出，说明书免费。
# 【args.vip 从哪来】对象 = 字典 + 类型标签；args.vip 本质是查 args.__dict__["vip"]，没有生成任何 def。
#   parse_args 内部：namespace = Namespace() 空袋子 → 对每个选项 setattr(namespace, "vip", True)。
#   setattr 让"属性名"可以是字符串——这就是运行期动态的秘密。
# 【status.split("(", 1)[1].rstrip(")")】以 "RE (ZeroDivisionError)" 为例分三步：
#   split("(",1) 按第一个"("切一刀 → ["RE ", "ZeroDivisionError)"]；
#   [1] 取第 2 块 → "ZeroDivisionError)"；rstrip(")") 剥掉右端")" → "ZeroDivisionError"。
#   split 的 1 = 最多切一刀，防止类型名里还有括号被切坏。
# 【复用/组合】ComplexityAnalyzer(generator, runner) 把现成的生成器和运行器"借"给分析器
#   （传的是同一个对象，不是复制品），计时与判定逻辑只写一份、两处同标准。
#   analyzer.analyze(SCALES) 再传三档规模 [300, 1000, 2000] 开始分析。
