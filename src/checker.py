# src/checker.py —— 对拍器：用"暴力解"当裁判，随机小样例双跑比对，抓 WA
from src.runner import CodeRunner

class Comparator:
    def __init__(self, generator, rounds=20, small_n=5, timeout=2.0):
        self.generator = generator   # 造数据用的
        self.rounds = rounds         # 对拍轮数（随机样例组数）
        self.small_n = small_n       # 每组规模：故意用小数据，暴力解才跑得动
        self.timeout = timeout       # 与 main 的 --timeout 同源

    def check(self, code_path, brute_path):
        print("=== 对拍模式 (WA 检测) ===")
        print(f"待测代码: {code_path}")
        print(f"暴力解(裁判): {brute_path}")
        print(f"随机样例: {self.rounds} 组，每组 N={self.small_n}")
        print()

        code_runner = CodeRunner(code_path, timeout=self.timeout)     # 一张图纸两辆车：各带各的路径
        brute_runner = CodeRunner(brute_path, timeout=self.timeout)

        for i in range(1, self.rounds + 1):
            arr = self.generator.generate_array(self.small_n)
            input_str = " ".join(map(str, arr))

            s1, _, out1 = code_runner.run_test(input_str)
            s2, _, out2 = brute_runner.run_test(input_str)

            if s1 != "Finished" or s2 != "Finished":
                # 有一边没跑完：RE/TLE 比对拍更基本，先报这个（裁判必须能跑完）
                print(f"第 {i} 组: 待测={s1}，暴力解={s2}")
                print(f"输入数据: {input_str}")
                print("对拍中止：先修掉 RE/TLE 再来抓 WA")
                return

            if out1 != out2:  # 逐字比对：连多空格、多换行都算错
                print(f"[WA] 第 {i} 组就抓到了！")
                print(f"输入数据: {input_str}")
                print(f"暴力解输出(期望): {out2}")
                print(f"待测代码输出(实际): {out1}")
                return

        print(f"[通过] {self.rounds} 组随机样例全部一致，未抓到 WA")

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
