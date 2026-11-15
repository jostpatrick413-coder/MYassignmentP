import os
import subprocess
import time

class CodeRunner:
    def __init__(self, code_path, timeout=2.0):  # 超过 2 秒判定为 TLE
        self.code_path = code_path
        self.timeout = timeout   # 超时阈值存起来，subprocess 和 TLE 判定共用

    def run_test(self, input_data):
        start_time = time.time()
        try:
            result = subprocess.run(   #终端py运行code
                ['python', self.code_path],
                input=input_data,
                text=True,             #按文本输入数据，并捕获输出
                capture_output=True,
                timeout=self.timeout,
                encoding="utf-8",      # 统一按 UTF-8 解码子进程的输出
                errors="replace",      # 解不了的字节用占位符代替，不让测试器崩掉
                env={**os.environ, "PYTHONIOENCODING": "utf-8"}  # 让子进程也按 UTF-8 输出
            )
            elapsed_time = time.time() - start_time

            if result.returncode != 0:  #报错
                error_type = extract_error_type(result.stderr)  # 从报错信息里挖出具体异常类型
                return f"RE ({error_type})", elapsed_time, result.stderr
            
            return "Finished", elapsed_time, result.stdout.strip()  #正常

        except subprocess.TimeoutExpired:  #超时
            return "TLE (Time Limit Exceeded)", self.timeout, "代码运行超时，可能有死循环！"
#subprocessrun：第一行，输入解释器和代码；
#第二行，输入input；
#第三行，文本编译，方便操作；
#第四行，拦截输出，装入result；
#第五行，超时哨卫————timeoutexpired
#result：returncode——怎么结束的；stdout，输出内容（带换行符）；stderr，报错信息
#time.time():标准计时刻

def extract_error_type(stderr_text):
    # traceback 最后一行形如 "ZeroDivisionError: division by zero"，挖出异常类型
    if not stderr_text:  # 极端情况（如输出解码失败）下 stderr 可能为空
        return "Runtime Error"
    for line in reversed(stderr_text.strip().splitlines()):
        for word in line.replace(":", " ").split():
            if word.endswith("Error") or word.endswith("Exception"):
                return word
    return "Runtime Error"
# ==== 学习笔记（本轮新增内容，精简版）====
# 【环境变量 os.environ】每个进程随身带一张"名字→值"的表；子进程出生时"复印"父进程的表（不是共享）。
#   改复印件不影响父进程，所以 env= 只影响这一个子进程，很安全。
# 【PYTHONIOENCODING】Python 写输出时的编码规则：表里有就照它，没有就按系统默认（中文 Windows=GBK）。
#   说话方和听话方编码不一致 → 乱码甚至 UnicodeDecodeError（本文件曾因此崩过，就是"编码炸弹"）。
# 【env={**os.environ, "PYTHONIOENCODING": "utf-8"}】"**"=拆包（把表里全部项铺开复制），再追加/覆盖一格。
#   必须整表复制：env 一旦给了，子进程"只用这张表"；漏带一项（如 SystemRoot）可能直接起不来。
# 【encoding="utf-8"】命令 subprocess 按 UTF-8 解码子进程输出的字节（管"听话的人"）。
# 【errors="replace"】遇到解不了的字节用占位符代替而不是崩溃——最后一道保险丝。
# 分工口诀：env 管说话的人用什么语言，encoding 管听话的人按什么语言听，errors 是保险丝。
# 【f-string】f"RE ({error_type})" 的 f 是格式化：把花括号里变量的值塞进字符串。不是正则！
# 【extract_error_type 思路】traceback 最后一行形如 "ZeroDivisionError: ..."：倒着逐行找
#   以 Error/Exception 结尾的词就是异常类型；stderr 为空（极端情况）兜底返回 "Runtime Error"。
