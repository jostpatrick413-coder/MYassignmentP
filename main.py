# main.py —— OJ 本地样例测试器 v1.0 的入口
from src.generator import DataGenerator
from src.runner import CodeRunner

N = 10   # 每组测试数据的规模，以后想测更大的数，改这里就行

def main():
    print("=== OJ 本地样例测试器 (v1.0) ===")
    print()

    generator = DataGenerator(min_val=1, max_val=100)   # 数据范围 1~100
    runner = CodeRunner("examples/demo_solution.py")    # 待测代码路径

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
        elif status == "RE (Runtime Error)":
            print(f"[运行时错误 RE] 耗时: {elapsed:.4f}s")
            print(f"报错信息: {output}")
        elif status == "TLE (Time Limit Exceeded)":
            print(f"[超时 TLE] 判定时间: {elapsed:.1f}s")
        print()

if __name__ == "__main__":
    main()
