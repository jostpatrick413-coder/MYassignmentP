# src/checker.py —— 对拍器：用"暴力解"当裁判，随机小样例双跑比对，抓 WA / 辨 PE
from src.runner import CodeRunner

def normalize(text):
    # 归一化：把任意连续空白（空格/换行/制表）折叠成单个空格，再掐头去尾
    # "46 5"、"46\n5"、"46\n\n5  " 归一化后都是 "46 5" —— 数值顺序不变，只洗摆法
    return " ".join(text.split())

class Comparator:
    def __init__(self, generator, rounds=20, small_n=5, timeout=2.0, validator=None):
        self.generator = generator   # 造数据用的
        self.rounds = rounds         # 对拍轮数（随机样例组数）
        self.small_n = small_n       # 每组规模：故意用小数据，暴力解才跑得动
        self.timeout = timeout       # 与 main 的 --timeout 同源
        self.validator = validator   # 可选：用户写的合法性校验器（None = 不校验）

    def check(self, code_path, brute_path):
        print("=== 对拍模式 (WA / PE 检测) ===")
        print(f"待测代码: {code_path}")
        print(f"暴力解(裁判): {brute_path}")
        print(f"随机样例: {self.rounds} 组，每组 N={self.small_n}")
        print()

        code_runner = CodeRunner(code_path, timeout=self.timeout)     # 一张图纸两辆车：各带各的路径
        brute_runner = CodeRunner(brute_path, timeout=self.timeout)

        compared = 0   # 实际完成比对的组数（跳过的不算）
        for i in range(1, self.rounds + 1):
            input_str = self._obtain_valid_input(brute_runner)
            if input_str is None:
                print(f"[跳过] 第 {i} 组：多次生成都未通过校验/裁判自检，数据疑似不合法")
                continue

            s1, _, out1 = code_runner.run_test(input_str)
            s2, _, out2 = brute_runner.run_test(input_str)

            if s1 != "Finished" or s2 != "Finished":
                # 有一边没跑完：RE/TLE 比对拍更基本，先报这个（裁判必须能跑完）
                print(f"第 {i} 组: 待测={s1}，暴力解={s2}")
                print(f"输入数据: {input_str}")
                print("对拍中止：先修掉 RE/TLE 再来抓 WA")
                return

            if out1 != out2:  # 逐字比对：连多空格、多换行都算不一致
                if normalize(out1) == normalize(out2):
                    # 归一化后一致 = 数值全对、只差空白摆法 → PE（格式错误），不是真 WA
                    print(f"[PE 格式错误] 第 {i} 组就抓到了！")
                    print(f"输入数据: {input_str}")
                    print("归一化后两边完全一致：数值全对，只差空白（空格/换行摆法）")
                    print(f"暴力解输出(期望,原始): {out2!r}")
                    print(f"待测代码输出(实际,原始): {out1!r}")
                    print("提示：逐字比对仍判不一致；各 OJ 对 PE 容忍度不同，以 OJ 判定为准")
                else:
                    print(f"[WA] 第 {i} 组就抓到了！")
                    print(f"输入数据: {input_str}")
                    print(f"暴力解输出(期望): {out2}")
                    print(f"待测代码输出(实际): {out1}")
                return
            compared += 1

        if compared == 0:
            print("[警告] 0 组完成比对：全部数据都没通过校验/裁判自检，先检查暴力解与数据约束")
        else:
            print(f"[通过] {compared} 组随机样例逐字全部一致，未抓到 WA/PE")

    def _obtain_valid_input(self, brute_runner):
        # 造数据 + 两道质量关：校验器（人写的谓词）先审，裁判（AC 代码）当探针再验
        for _ in range(10):   # 每组最多重造 10 次
            arr = self.generator.generate_array(self.small_n)
            input_str = " ".join(map(str, arr))
            if self.validator and not self.validator.validate(input_str):
                print("[校验未通过] 重造")
                continue
            status, _, _ = brute_runner.run_test(input_str)
            if not status.startswith("Finished"):
                # AC 代码在合法数据上一定正常跑完；裁判自己都跑挂 = 数据疑似不合法
                print(f"[疑似不合法] 裁判在本组数据上报错（{status}），重造")
                continue
            return input_str
        return None   # 重试耗尽：这组放弃

# ==== 学习笔记（本文件全解，精简版）====
# 【对拍思想】同一份输入喂两份代码：待测 + 暴力解（裁判）。输出不一致 → 待测 WA。
#   裁判要"笨但一定对"：把题意原封不动写成代码，放弃一切优化（O(N²) 也允许）。
# 【为什么用小数据】暴力解可能很慢，N 小它才秒跑；对拍要的是"样例多、覆盖广"，不是"数据大"。
# 【为什么逐字比字符串】多一个空格、多一行空行都会判 WA —— 顺带抓"输出格式错误"。
# 【裁判必须先跑完】哪边 RE/TLE 就先报哪个；裁判坏了，对拍没有意义。
# 【s1, _, out1】下划线 _ 表示"这个返回值我不需要"，占个位置；out1/out2 才是要比对的东西。
# 【一个类、两个实例】CodeRunner 是图纸，code_runner / brute_runner 是按图纸造出的两辆车，各带各的路径。
# ==== 学习笔记（本轮新增，精简版）====
# 【对拍输出天然可复现】checker 不打印耗时（只报输入、两边输出、WA），所以同 seed 下两次对拍
#   完整输出逐字一致——验证"种子可复现"时，对拍模式是最干净的比对对象（无墙钟噪声混入）。
# ==== 学习笔记（PE 检测本轮新增，精简版）====
# 【归一化】normalize = " ".join(text.split())：split() 不带参数 = 按"任意连续空白"切词
#   （空格/换行/制表都算、连成一片算一刀）；join 用单个空格拼回。效果：所有空白折叠成一个空格。
# 【三层判定】逐字一致 → 通过；逐字不同但归一化一致 → PE（数值全对、只差摆法）；
#   归一化仍不同 → 真 WA。黑箱被拆成三层，PE 不再是冷冰冰的 WA。
# 【!r = repr】f"{out2!r}" 让字符串里看不见的字符显形：\n 显示成 \n、空格原样可见。
#   报告里摆出两边的"原始长相"，PE 差异一眼看清——透明报告的关键一招。
# 【归一化不会洗白 WA】它只折叠空白、绝不碰数字：数值错就是错，折叠后照样对不上。
# 【边界】runner 收到子进程输出时已 strip() 掐头去尾，"末尾多空行/行尾多空格"进比对前就没了；
#   本工具的 PE 检测聚焦"输出内部"的空白差异；各 OJ 对 PE 容忍度不同，诊断仅供参考、以 OJ 为准。
# ==== 学习笔记（裁判探针本轮新增，精简版）====
# 【为什么要裁判当探针】校验器（人写的谓词）审的是"人记得住的约束"；题意的完整约束
#   编译在 AC 代码里。合法数据上 AC 代码一定正常跑完——它自己跑挂（RE/TLE）= 数据疑似不合法。
#   裁判免费当第二道质量关，堵住"校验器漏写的约束"（如"三个数必须能构成三角形"这种藏在题意深处的规则）。
# 【先审后验】校验器在前（纯函数、毫秒级），裁判在后（要开子进程、慢得多）：
#   便宜的关卡先拦掉大部分废数据，贵的探针只面对"看起来合法"的候选。
# 【返回契约】_obtain_valid_input 成功 = 输入字符串；重试耗尽 = None。调用方 if input_str is None
#   就跳过这一组——对拍不因个别坏数据组停摆，只是"这组不比"。
# 【compared 诚实计数】只统计真正完成比对的组；0 组时单独报警告而不是"[通过] 0 组"——
#   "通过 0 组"是自相矛盾的话，真相是"没有样本可比对"，矛头指向暴力解或数据约束。
