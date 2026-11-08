# src/analyzer.py —— 复杂度分析器：多档规模计时，用增速估算复杂度
import math

class ComplexityAnalyzer:
    def __init__(self, generator, runner, repeat=3):
        self.generator = generator   # 造数据用的，按档位生成对应规模的输入
        self.runner = runner         # 跑代码用的，复用 CodeRunner 的计时与判定
        self.repeat = repeat         # 每档重复次数，取最快的一次（减少噪声）

    def analyze(self, scales):
        print("=== 复杂度分析 ===")
        baseline = self._measure_baseline()  # 先测出"与数据量无关"的固定开销
        times = []
        for n in scales:
            input_str = " ".join(map(str, self.generator.generate_array(n)))
            best = float("inf")
            status = "Finished"
            for _ in range(self.repeat):
                s, t, _ = self.runner.run_test(input_str)
                if not s.startswith("Finished"):
                    status, best = s, t   # TLE 或 RE，这一档就没法分析了
                    break
                best = min(best, t)
            adjusted = max(best - baseline, 0.0001)  # 扣掉启动开销，至少保留一个极小值
            times.append(adjusted)
            if status == "Finished":
                print(f"  N={n:<6d} 耗时: {best:.4f}s → 扣基线后 {adjusted:.4f}s")
            else:
                print(f"  N={n:<6d} {status}，分析中止")
                return
        self._estimate(scales, times)

    def _measure_baseline(self):
        # 用最小规模测固定开销（主要是子进程启动），后续从每档耗时里扣掉
        input_str = " ".join(map(str, self.generator.generate_array(10)))
        best = float("inf")
        for _ in range(self.repeat):
            s, t, _ = self.runner.run_test(input_str)
            if not s.startswith("Finished"):
                return 0.0   # 代码连小数据都跑不过，干脆不校准
            best = min(best, t)
        return best

    def _estimate(self, scales, times):
        # 核心思想：耗时比 ÷ 规模比 ≈ 增长幂次
        # O(N) 代码规模翻 k 倍耗时也翻 k 倍（幂次≈1）；O(N^2) 则翻 k^2 倍（幂次≈2）
        exps = []
        for i in range(1, len(scales)):
            if times[i - 1] <= 0.0002:  # 前档耗时才到保底值，说明还在噪声区，跳过这一对
                continue
            n_ratio = scales[i] / scales[i - 1]
            t_ratio = times[i] / times[i - 1]
            exps.append(math.log(t_ratio) / math.log(n_ratio))
        if not exps:
            print("  耗时数据不足，无法估算（代码跑得太快，测量值全在噪声区）。")
            return
        print(f"  相邻档位增长幂次: {[round(e, 2) for e in exps]}")
        avg_exp = sum(exps) / len(exps)
        if max(times) < 0.05:
            print("  提示：扣掉启动开销后耗时仍都低于 0.05s，说明待测代码太快，")
            print("        测量结果会偏向 O(1)。想测出真实复杂度请换更耗时的代码或加大规模。")
            return
        if avg_exp <= 0.5:
            print("  结论: 接近 O(1)（或耗时被启动开销掩盖）")
        elif avg_exp < 1.6:
            print("  结论: 大致 O(N)，线性增长，比较安全")
        elif avg_exp < 2.6:
            print("  结论: 大致 O(N^2)，规模翻倍耗时约翻 4 倍，注意 TLE 风险")
        else:
            print("  结论: 高于 O(N^2)，极可能有 TLE 风险！")
# ==== 学习笔记（本文件全解，精简版）====
# 【基线校准】子进程启动有固定开销(约0.03s)、与数据量无关。先用 N=10 测出基线，每档耗时扣掉它。
#   类比电子秤"去皮"：容器重量不算进货物。
# 【取最快】每档跑 repeat 次取 min：慢的那几次多半是别的程序抢了 CPU，最快的才接近真实耗时。
# 【垫底 max(..., 0.0001)】扣基线可能得 0/负数，而 log(0) 会炸，垫个极小值保底。
# 【幂次公式】增长幂次 = log(耗时比) ÷ log(规模比)。
#   O(N) 代码规模翻 k 倍、耗时也翻 k 倍（幂次≈1）；O(N²) 翻 k² 倍（幂次≈2）。
#   log 是"几次方"：log(9)÷log(3)=2，因为 3²=9。
# 【噪声守卫】前档耗时才到保底值(≤0.0002)说明还在噪声区，比值不可信，跳过这一对。
# 【分级】平均幂次 ≤0.5→接近O(1)；0.5~1.6→O(N)；1.6~2.6→O(N²)；更大→高危。
# 【诚实提示】扣基线后仍全<0.05s = 代码太快测不出，明说"偏向 O(1)"，不硬编结论。
