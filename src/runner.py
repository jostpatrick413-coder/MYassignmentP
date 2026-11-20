import os
import subprocess
import time
import re

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

def extract_crash_location(stderr_text):
    # 从 traceback 文本里提炼崩溃位置：格式固定为 '  File "文件", line 行号, in 函数'
    # 最后一处 File 行 = 真正崩掉的那一帧（前面的是调用链上"路过"的帧）
    if not stderr_text:
        return None
    pattern = re.compile(r'^  File "(.+)", line (\d+), in ')
    lines = stderr_text.splitlines()
    frame = None
    for idx, line in enumerate(lines):
        m = pattern.match(line)
        if m:
            frame = m.group(1), int(m.group(2)), idx   # 记住最新一次命中，就是最后一帧
    if frame is None:
        return None   # 不是标准 traceback，返回 None 让报告照旧打印全文
    fname, lineno, idx = frame
    code_line = ""
    if idx + 1 < len(lines) and lines[idx + 1][:1] in (" ", "\t"):
        code_line = lines[idx + 1]   # File 行下一行就是出错源码；traceback 里源码行必缩进
    return fname, lineno, code_line
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
# ==== 学习笔记（本轮新增，精简版）====
# 【墙钟噪声】time.time() 测的是物理时间的真实流逝，CPU 忙闲都会影响它：同一份代码每次耗时都不同，
#   而且与随机种子无关——种子固定的是数据流，不是时钟。计时永远是带噪声的测量。
# ==== 学习笔记（RE 结构化报告本轮新增，精简版）====
# 【traceback 文本格式】报错文本的格式是 Python 承诺的："  File \"文件\", line 行号, in 函数"。
#   标准库有 from_exception（吃活异常对象），却没有公开的"文本→结构"解析器（实测 from_string 不存在），
#   所以自己写迷你解析器：按承诺的格式用正则逐行找 File 行。
# 【最后一处 File 行】traceback 从外到内列调用链，最后一处 File 行 = 真正崩掉的那一帧，
#   前面的帧只是"路过"。所以解析时"记住最新的一次命中"即可，不用知道后面还有没有。
# 【源码行必缩进】File 行的下一行就是出错那行源码；traceback 里源码行一定带缩进，
#   而异常消息行顶格——用"下一行首字符是不是空白"来甄别，比判断内容更稳。
# 【parse 不到就 None】stderr 为空或格式不标准就返回 None，调用方走 if loc 兜底照旧打印全文：
#   诊断是加分项，绝不能因为解析失败把报告搞崩。
# 【为什么不改 run_test 返回值】让 main 自己解析 stderr（第 3 个返回值里就有全文），
#   checker/analyzer 的 3 元组解包零改动——最小侵入，老调用方不陪跑。
# ==== 学习笔记（正则解剖，随问随记）====
# 【正则 = 形状模板】pattern 描述的是一类文字的"轮廓"，不是某一段具体文字。match() 拿模板从头量一行，
#   量得上返回 Match 对象（还能掏出括号里兜住的部分），量不上返回 None。
# 【r 前缀】r'...' 原始字符串：反斜杠原样交给正则引擎，不让 Python 先按自己的转义规则处理（\d 才保得住）。
# 【逐件拆】^ = 只认行首；'  File "' = 两个空格 + File + 引号（traceback 承诺的固定格式）；
#   (.+) = 括号 1 号兜住"任意字符、至少 1 个"（文件名）；(\d+) = 括号 2 号兜住"至少 1 个数字"（行号）；
#   ', in ' = 收尾的路标。实例：'  File "x.py", line 3, in <module>' → group(1)="x.py"，group(2)="3"。
# 【group 取货】括号 = 捕鼠夹，group(1) 是 1 号夹兜住的东西。夹到的行号还是字符串，int() 转成数字。
# 【match ≠ search】match 只从行首开始量（^ 等于再钉一遍）；search 是满行找。这里必须用 match：
#   异常消息行或源码行里若碰巧出现 "File" 字样，search 会误伤。
