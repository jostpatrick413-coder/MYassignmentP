# main.py —— OJ 本地样例测试器 v1.0 的入口
import sys
from src.generator import DataGenerator
from src.runner import CodeRunner
from src.analyzer import ComplexityAnalyzer

N = 10   # 每组测试数据的规模，以后想测更大的数，改这里就行
ANALYZE = True               # 跑完 5 组用例后，是否追加复杂度分析
SCALES = [300, 1000, 2000]   # 复杂度分析的三档规模（小/中/大）

def main():
    print("=== OJ 本地样例测试器 (v1.0) ===")
    print()

    # sys.argv 是命令行参数列表，argv[0] 是脚本名本身
    # 这样测试任意代码就不用改文件了：python main.py examples/demo_rte.py
    code_path = sys.argv[1] if len(sys.argv) > 1 else "examples/demo_solution.py"

    generator = DataGenerator(min_val=1, max_val=100)   # 数据范围 1~100
    runner = CodeRunner(code_path)                      # 待测代码路径（可在命令行指定）

    test_cases = generator.generate_edge_cases(N)       # 4 组边界用例
    test_cases["random_case"] = generator.generate_array(N)  # 再加 1 组随机用例

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

    if ANALYZE:
        analyzer = ComplexityAnalyzer(generator, runner)  # 分析器复用同一个生成器与运行器
        analyzer.analyze(SCALES)

if __name__ == "__main__":
    main()
#我将花费一个学期理解这个代码。这个import让我认识到库是一个py可调用的代码群，所以我可以自己写一些库参与项目。
#然后是这种文件间的配合很有工程之美，从DG和CR里分别造数据和启动待测代码并接住返回的数据。
# ==== 学习笔记（本轮新增内容，精简版）====
# 【sys.argv】命令行参数列表：argv[0]=脚本名本身，argv[1]=第一个参数。
#   python main.py examples/demo_rte.py → argv[1]="examples/demo_rte.py"。
#   三元表达式 X if 条件 else Y：有参数就用 argv[1]，没有就退回默认示例代码。
# 【status.split("(", 1)[1].rstrip(")")】以 "RE (ZeroDivisionError)" 为例分三步：
#   split("(",1) 按第一个"("切一刀 → ["RE ", "ZeroDivisionError)"]；
#   [1] 取第 2 块 → "ZeroDivisionError)"；rstrip(")") 剥掉右端")" → "ZeroDivisionError"。
#   split 的 1 = 最多切一刀，防止类型名里还有括号被切坏。
# 【复用/组合】ComplexityAnalyzer(generator, runner) 把现成的生成器和运行器"借"给分析器
#   （传的是同一个对象，不是复制品），计时与判定逻辑只写一份、两处同标准。
#   analyzer.analyze(SCALES) 再传三档规模 [300, 1000, 2000] 开始分析。
