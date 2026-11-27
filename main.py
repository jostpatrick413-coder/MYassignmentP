# main.py —— OJ 本地样例测试器 v1.2 的入口
import argparse
import os
from src.generator import DataGenerator
from src.runner import CodeRunner, extract_crash_location
from src.analyzer import ComplexityAnalyzer
from src.checker import Comparator
from src.validator import InputValidator

SCALES = [300, 1000, 2000]   # 复杂度分析的三档规模（小/中/大）

def parse_count(text):
    # 行数/每行输入数旋钮："3" → 固定 3；"2-5" → (2,5) 表示每次掷 2~5
    if "-" in text and not text.startswith("-"):
        parts = text.split("-")
        if len(parts) != 2:
            raise argparse.ArgumentTypeError(f"范围应为 小-大（如 2-5），收到: {text}")
        try:
            lo, hi = int(parts[0]), int(parts[1])
        except ValueError:
            raise argparse.ArgumentTypeError(f"范围两端应为整数（如 2-5），收到: {text}")
        if lo > hi:
            raise argparse.ArgumentTypeError(f"范围左端不能大于右端（收到: {text}）")
        return (lo, hi)
    try:
        n = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"应为整数或 小-大 范围（如 3 或 2-5），收到: {text}")
    if n < 0:
        raise argparse.ArgumentTypeError(f"行数/输入数不能为负（收到: {text}）")
    return n

def main():
    # argparse 四步：造"菜单簿" → 登记规则 → 解析 → 取值
    parser = argparse.ArgumentParser(description="OJ 本地样例测试器：生成数据、跑代码、判 RE/TLE/WA")
    # 输入行数：整数或范围（范围 = 每个用例掷一次，0 行即空输入）
    parser.add_argument("--rows", type=parse_count, default=1, help="输入行数：整数或范围（如 3 或 2-5），默认 1 行")
    # 每组测试数据的规模，以后想测更大的数，改这里就行
    parser.add_argument("--n", type=parse_count, default=10, help="每行输入数：整数或范围（如 10 或 2-8），默认 10")
    # 跑完 5 组用例后，是否追加复杂度分析
    parser.add_argument("--analyze", action="store_true", default=True, help="追加复杂度分析（默认开启）")
    parser.add_argument("--no-analyze", dest="analyze", action="store_false", help="跳过复杂度分析")
    parser.add_argument("--code", default=None, help="待测代码路径（缺省：有 --pid 用 <题号>.py，否则 demo_solution）")
    parser.add_argument("--min", type=int, default=1, help="随机数据最小值")
    parser.add_argument("--max", type=int, default=100, help="随机数据最大值")
    parser.add_argument("--alphabet", default=None, help="符号输入：字符集合（如 +-*/ 或 abc），给了它就不再掷整数")
    parser.add_argument("--header", action="store_true", help="首行参数模式：第一行 N（按 --n 掷），第二行 N 个值；此模式忽略 --rows")
    parser.add_argument("--seed", type=int, default=None, help="随机种子：同一 seed 每次生成相同数据（抓 WA 后可复现）")
    parser.add_argument("--timeout", type=float, default=2.0, help="单组超时阈值（秒）")
    parser.add_argument("--check", action="store_true", help="开启对拍模式（WA / PE 检测）")
    parser.add_argument("--brute", default=None, help="对拍裁判（暴力解）路径，缺省按 --pid 找 solutions/<题号>.py")
    parser.add_argument("--pid", type=int, default=None, help="题号：按约定自动定位待测代码与裁判")
    parser.add_argument("--validator", default=None, help="校验器脚本路径：需定义 is_valid(输入文本) → True/False，不合法数据自动重造")
    args = parser.parse_args()   # 解析：命令行原始字符串对照规则，结果装进 args 托盘

    # 待测代码三选一：--code 显式给 > 按 --pid 拼 "题号.py" > 默认 demo
    code_path = args.code or (f"{args.pid}.py" if args.pid else "examples/demo_solution.py")
    if not os.path.exists(code_path):
        print(f"找不到待测代码: {code_path}（约定：按题号命名，如 30012.py）")
        return
    if args.validator and not os.path.exists(args.validator):
        print(f"找不到校验器: {args.validator}（脚本需定义 is_valid(输入文本) 函数）")
        return

    print("=== OJ 本地样例测试器 (v1.2) ===")
    print()

    generator = DataGenerator(min_val=args.min, max_val=args.max, seed=args.seed, rows=args.rows, cols=args.n, alphabet=args.alphabet, header=args.header)  # 数据范围与种子都来自命令行
    runner = CodeRunner(code_path, timeout=args.timeout)            # 待测代码与超时都来自命令行
    validator = InputValidator(args.validator) if args.validator else None  # 校验器：人写的合法性谓词

    if args.check:
        # 裁判三选一：--brute 显式给 > 按 --pid 找 solutions/<题号>.py > 默认 demo
        brute_path = args.brute or (f"solutions/{args.pid}.py" if args.pid else "examples/demo_solution.py")
        if not os.path.exists(brute_path):
            print(f"找不到裁判: {brute_path}")
            print("对拍需要一份你确信正确的解：把你 AC 过的代码存进 solutions/（文件名 = 题号）")
            return
        Comparator(generator, rounds=20, small_n=5, timeout=args.timeout, validator=validator).check(code_path, brute_path)
        return

    test_cases = generator.generate_edge_cases()       # 9 组边界用例（矩形模型，形状按旋钮掷）
    test_cases["random_case"] = generator.make_case("random_case")  # 再加 1 组随机用例（行数与每行个数都按旋钮）

    for name, grid in test_cases.items():                # 逐个用例测试
        input_str = "\n".join(" ".join(map(str, row)) for row in grid)  # 把列表拼成 "3 1 4 ..." 形式的字符串
        if validator:
            for attempt in range(1, validator.max_tries + 1):
                if validator.validate(input_str):
                    break                                # 合法：跳出重试，正常开测
                print(f"[校验未通过] {name} 第 {attempt} 次重造")   # 不合法：重掷形状与数值
                grid = generator.make_case(name)
                input_str = "\n".join(" ".join(map(str, row)) for row in grid)
            else:
                # for-else：循环跑满 max_tries 次、一次都没 break = 重试耗尽
                print(f"--- 正在测试: {name} ---")
                print(f"[跳过] 重试 {validator.max_tries} 次都未通过校验器：约束与数据形状可能冲突")
                print()
                continue
        print(f"--- 正在测试: {name} ---")
        print(f"输入数据 ({len(grid)} 行): {input_str if input_str else '(空输入)'}")  # 0 行显示 (空输入)，不然只剩孤零零的"输入数据"

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
# 【三元表达式】input_str if input_str else '(空输入)'：if 是"真"就用它自己，否则用备胎文案。
#   0 行拼出来是空字符串 ""，而 "" 是"假"——所以它顺手兼任了"判空开关"。
#   一个字符串的真假 = 它长不长（非空为真）；同理 0、None、[] 都是"假"。
# 【职责分工】runner 管"挖"：extract_crash_location 从报错文本里提炼出 (文件名, 行号, 出错代码)；
#   main 管"摆"：拿到三元组后决定怎么打印。挖不到就返回 None，main 走 if loc 兜底，照旧打印全文。
#   好处：谁也不用知道对方内部的脏活——main 只认"要么三元组、要么 None"这一张名片。
# ==== 学习笔记（矩形模型本轮新增，精简版）====
# 【parse_count 职责】把命令行的旋钮文本变成 int（固定）或 tuple（范围）。放在 main 而不是 generator：
#   解析命令行是 main 的分内事，generator 只管"拿到 spec 之后怎么掷"——造数据的不知道也不关心文本长啥样。
# 【ArgumentTypeError】type= 的解析函数报错就用 argparse.ArgumentTypeError：argparse 会接住它，
#   自动打印"参数名 + 错误消息 + 用法提示"并退出，比手写 print 再 exit 地道。
# 【'-' 的歧义】"2-5" 里 '-' 是范围符；"-3" 里 '-' 是负号。用 startswith("-") 区分；
#   范围还要拦三个错：不是两段、两端不是整数、左大右小。
# 【嵌套 join】"\n".join(" ".join(map(str,row)) for row in grid)：内层把每行拼空格，外层把行拼换行。
#   生成器表达式 (… for row in grid) 不占内存、逐个喂给外层 join。
# 【(N 行) 前缀】显示行数让用户一眼看出这组用例的形状；多行输入自带换行，终端直接竖着排。
# ==== 学习笔记（符号输入轮本轮新增，精简版）====
# 【--alphabet 只是值旋钮】加符号模式时 main 只多了两行：登记参数、传给 DataGenerator。
#   报告/对拍/校验器全都不用改——因为它们只搬运和比对文本，不关心内容是数字还是符号。
# ==== 学习笔记（校验器接线本轮新增，精简版）====
# 【可选外挂】validator = InputValidator(路径) if args.validator else None：没给 --validator 就得到 None，
#   后面所有 if validator / self.validator 短路跳过——校验器是外挂，不装主流程照跑。
# 【for-else】else 挂在 for 上：循环"自然跑完"（一次都没 break）才进 else。这里用它表达
#   "重试 max_tries 次全失败"——任何一次成功都 break 跳出，else 只留给"全灭"收尸。
#   只有 break 会绕过 else；continue 只是跳过本轮、循环照跑，跑满次数照样进 else。
#   本处流程：校验失败 → 重造数据 → 循环继续；耗尽后 else 打印跳过，continue 的是外层用例循环。
# 【冲突报告】"[跳过] 约束与数据形状可能冲突"：校验器永远拒绝某种形状（如"必须非空" × 空数组用例），
#   重试一万次也没用——诚实报告"可能冲突"而不是无限重试，判断权交回用户。
# ==== 学习笔记（首行参数轮本轮新增，精简版）====
# 【--header 只是模板开关】加首行参数模式时 main 只多两行：登记开关、传给 DataGenerator。
#   与 --alphabet 一模一样的接法——main 的职责就是"把旋钮递给生成器"，模板内部怎么摆是 generator 的事。
# 【开关的 help 要写代价】"--rows 失效"直接写进 --header 的帮助文案：约定优于配置，但"旋钮失效"
#   必须预先声明，用户才知道这个开关的完整语义。
