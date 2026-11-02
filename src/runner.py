import subprocess
import time

class CodeRunner:
    def __init__(self, code_path):
        self.code_path = code_path

    def run_test(self, input_data):
        start_time = time.time()
        try:
            result = subprocess.run(   #终端py运行code
                ['python', self.code_path],
                input=input_data,
                text=True,             #按文本输入数据，并捕获输出
                capture_output=True,
                timeout=2.0  # 超过 2 秒判定为 TLE
            )
            elapsed_time = time.time() - start_time

            if result.returncode != 0:  #报错
                return "RE (Runtime Error)", elapsed_time, result.stderr
            
            return "Finished", elapsed_time, result.stdout.strip()  #正常

        except subprocess.TimeoutExpired:  #超时
            return "TLE (Time Limit Exceeded)", 2.0, "代码运行超时，可能有死循环！"
#subprocessrun：第一行，输入解释器和代码；
#第二行，输入input；
#第三行，文本编译，方便操作；
#第四行，拦截输出，装入result；
#第五行，超时哨卫————timeoutexpired
#result：returncode——怎么结束的；stdout，输出内容（带换行符）；stderr，报错信息
#time.time():标准计时刻