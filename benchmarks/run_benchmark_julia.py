import numpy as np
import subprocess
import json
import matplotlib
import matplotlib.pyplot as plt

NM = range(2,150,4)
# NM = range(2,20,2)
NREP_small = 10000
NREP_medium = 100
NREP_large = 10
AVG_CPU_TIME = []
res_file = 'riccati_benchmark_julia.json'
RUN = True
UPDATE_res = True

if not UPDATE_res:
    print('Warning: not updating result file!')

if RUN:
    for i in range(len(NM)):
        print('running Riccati benchmark for case NM = {}'.format(NM[i]))
        code = ""
        if NM[i] < 30:
            NREP = NREP_small
        elif NM[i] < 100:
            NREP = NREP_medium
        else:
            NREP = NREP_large

        with open('test_riccati.jl.in') as template:
            code  = template.read()
            code = code.replace('NM', str(NM[i]))
            code = code.replace('NREP', str(NREP))

        with open('test_riccati.jl', 'w+') as bench_file:
            bench_file.write(code)

        cmd = 'julia test_riccati.jl'
        proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)

        try:
            outs, errs = proc.communicate()
        except TimeOutExpired:
            proc.kill()
            print('Exception raised at NM = {}'.format(NM[i]))
            outs, errs = proc.communicate()

        AVG_CPU_TIME.append([float(outs.decode()), NM[i]])

    if UPDATE_res:
        with open(res_file, 'w+') as res:
            json.dump(AVG_CPU_TIME, res)
