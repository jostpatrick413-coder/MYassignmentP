# main.py —— OJ 本地样例测试器 v1.2 的入口
import argparse
import os
from src.generator import DataGenerator
from src.runner import CodeRunner, extract_crash_location
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
    parser.add_argument("--code", default=None, help="待测代码路径（缺省：有 --pid 用 <题号>.py，否则 demo_solution）")
    parser.add_argument("--min", type=int, default=1, help="随机数据最小值")
    parser.add_argument("--max", type=int, default=100, help="随机数据最大值")
    parser.add_argument("--seed", type=int, default=None, help="随机种子：同一 seed 每次生成相同数据（抓 WA 后可复现）")
    parser.add_argument("--timeout", type=float, default=2.0, help="单组超时阈值（秒）")
    parser.add_argument("--check", action="store_true", help="开启对拍模式（WA / PE 检测）")
    parser.add_argument("--brute", default=None, help="对拍裁判（暴力解）路径，缺省按 --pid 找 solutions/<题号>.py")
    parser.add_argument("--pid", type=int, default=None, help="题号：按约定自动定位待测代码与裁判")
    args = parser.parse_args()   # 解析：命令行原始字符串对照规则，结果装进 args 托盘

    # 待测代码三选一：--code 显式给 > 按 --pid 拼 "题号.py" > 默认 demo
    code_path = args.code or (f"{args.pid}.py" if args.pid else "examples/demo_solution.py")
    if not os.path.exists(code_path):
        print(f"找不到待测代码: {code_path}（约定：按题号命名，如 30012.py）")
        return

    print("=== OJ 本地样例测试器 (v1.2) ===")
    print()

    generator = DataGenerator(min_val=args.min, max_val=args.max, seed=args.seed)  # 数据范围与种子都来自命令行
    runner = CodeRunner(code_path, timeout=args.timeout)            # 待测代码与超时都来自命令行

    if args.check:
        # 裁判三选一：--brute 显式给 > 按 --pid 找 solutions/<题号>.py > 默认 demo
        brute_path = args.brute or (f"solutions/{args.pid}.py" if args.pid else "examples/demo_solution.py")
        if not os.path.exists(brute_path):
            print(f"找不到裁判: {brute_path}")
            print("对拍需要一份你确信正确的解：把你 AC 过的代码存进 solutions/（文件名 = 题号）")
            return
        Comparator(generator, rounds=20, small_n=5, timeout=args.timeout).check(code_path, brute_path)
        return

    test_cases = generator.generate_edge_cases(args.n)       # 4 组边界用例
    test_cases["random_case"] = generator.generate_array(args.n)  # 再加 1 组随机用例

    for name, arr in test_cases.items():                # 逐个用例测试
        input_str = " ".join(map(str, arr))             # 把列表拼成 "3 1 4 ..." 形式的字符串
        print(f"--- 正在测试: {name} ---")
        print(f"输入数据: {input_str if input_str else '(空数组)'}")   # 空数组显示 (空数组)，不然只剩孤零零的"输入数据:"

        status, elapsed, output = runner.run_test(input_str)  # 核心：调用你的 runner

        if status == "Finished":
            print(f"[通过] 耗时: {elapsed:.4f}s")
            print(f"程序输出: {output}")
        elif status.startswith("RE"):
            error_name = status.split("(", 1)[1].rstrip(")")  # 括号里是具体异常类型
            print(f"[运行时错误] {error_name}  耗时: {elapsed:.4f}s")
            loc = extract_crash_location(output)              # 从 traceback 里提炼崩溃位置
            if loc:
                fname, lineno, code_line = loc
                print(f"崩溃位置: {fname} 第 {lineno} 行")
                if code_line:
                    print(f"出错代码: {code_line.strip()}")
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
# 【--pid 题号约定】约定优于配置：不传一堆路径，只报题号，按约定位置自动找文件。
#   待测默认 "<题号>.py"（当前目录），裁判默认 "solutions/<题号>.py"。
# 【args.code or (…)】or 的短路：左边是 None（"假"）就返回右边，否则返回左边——链式兜底。
# 【f"{args.pid}.py"】路径是拼出来的字符串：30012 → "30012.py"；f"solutions/{args.pid}.py" 同理。
# 【os.path.exists(路径)】问操作系统"这个文件在不在"，返回 True/False。
#   先检查再运行：subprocess 找不到文件只会吐一堆报错，先检查能给出友好提示。
# 【.gitignore】列在里面的路径 git 视而不见：solutions/ 题库只留本地，不进公开仓库（学术诚信）。
# 【os 模块】os = operating system，Python 与操作系统的传话筒：问文件、列目录、看环境变量。
#   模块里装着两种东西：函数（动词，如 os.path.exists）和数据（名词，如 os.environ）。
#   os.path 是子模块（模块套模块），专管路径这一摊事。
# 【os.path.exists(路径)】问"这文件在不在"，只回答 True/False——只问不碰，不打开不读内容。
#   配套：os.path.isfile 只认文件、os.path.isdir 只认文件夹、os.path.join 按系统规范拼路径
#   （Windows 反斜杠 / Linux 正斜杠，比手拼 f-string 更稳）、os.getcwd 当前目录、os.listdir 列目录。
# 【if not os.path.exists(...): return】卫语句（guard clause）：先把异常情况在门口拦掉，
#   主流程就不用裹进层层 if-else。类比门卫：没证件直接请回。
# 【自学招】dir(模块) 列全部成员；help(函数) 或 函数.__doc__ 看自带说明书。
# ==== 学习笔记（--seed 本轮新增，精简版）====
# 【可复现性】随机样例最大的敌人是"跑了就没了"：这次抓的 WA 下次重现不了。
#   固定种子后同一命令重跑，输入数据逐字节相同——复现、截图、发给同学，都是同一份。
# 【seed 传递链】命令行 --seed → args.seed → DataGenerator(seed=...) → random.seed()。
#   普通测试与对拍共用一个 generator 对象，所以一个参数、两处同时生效。
# 【type=int + default=None】与 --pid 同一配方：整数校验 + None 表示"未指定"。None 是"假"，
#   所以还能塞进 args.code or ... 这类短路链里继续兜底。
# ==== 学习笔记（实测与验证方法，本轮新增，精简版）====
# 【种子管数据，不管耗时】同 seed 保证"输入数据"逐字一致；耗时是墙钟时间（物理世界真实流逝），
#   不是随机数，种子管不着。验证可复现性只比数据行，不比耗时行。
# 【测试命令四件套】| 管道=水管（左边程序的打印接给右边当输入）；grep=滤网（只放行含关键词的行）；
#   2>&1=并流阀（2号报错口并进1号正常口，管道默认只接1号口）；$(...)=接水桶（把结果存进变量）。
# 【命令与项目的关系】测试命令是"遥控器"，项目是"电视机"：唯一接触点 = main.py 的命令行界面，
#   方向单向、从外向内；项目只管 print，不知道谁在看。外部命令依赖输出格式（契约）——
#   改 print 的文字，靠它吃饭的 grep 就会失明。
# ==== 学习笔记（边界补全与 RE 结构化报告，本轮新增，精简版）====
# 【三元表达式】input_str if input_str else '(空数组)'：if 是"真"就用它自己，否则用备胎文案。
#   空数组 join 出来是空字符串 ""，而 "" 是"假"——所以它顺手兼任了"判空开关"。
#   一个字符串的真假 = 它长不长（非空为真）；同理 0、None、[] 都是"假"。
# 【职责分工】runner 管"挖"：extract_crash_location 从报错文本里提炼出 (文件名, 行号, 出错代码)；
#   main 管"摆"：拿到三元组后决定怎么打印。挖不到就返回 None，main 走 if loc 兜底，照旧打印全文。
#   好处：谁也不用知道对方内部的脏活——main 只认"要么三元组、要么 None"这一张名片。
