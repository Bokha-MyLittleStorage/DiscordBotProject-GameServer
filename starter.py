import subprocess
import concurrent.futures
import os

# failed attempt
'''
def main_parallel_run():
    #env = os.environ
    #print(env['PATH']) 
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=10)
    targets = ['GameServerBot-v3.1-r220319.botTokenHidden.py', 'CoinChanger-v1.2-r220521.py']
    procs = []
    for single_run in enumerate(targets):
        procs.append(executor.submit(subprocess.run, single_run , shell=True, capture_output=True, text=True))

    concurrent.futures.wait(procs)

if __name__ == '__main__': main_parallel_run()
'''

targets = ['GameServerBot-v3.1-r220319.botTokenHidden.py', 'CoinChanger-v1.2-r220521.py']
for target in targets: os.startfile('.\\GameServerBot-v3.1-r220319.botTokenHidden.py')
