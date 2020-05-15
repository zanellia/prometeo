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
res_file = 'riccati_benchmark_prometeo.json'
RUN = False
UPDATE_res = False
UPDATE_FIGURE = True
figname = 'riccati_benchmark'

blasfeo_res_file = 'riccati_benchmark_blasfeo_api.json'
LOAD_BLASFEO_RES = True

if not UPDATE_res:
    print('Warning: not updating result file! This will just '
        'plot the results at the end of the benchmark.')

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

        with open('riccati_mass_spring.py.in') as template:
            code  = template.read()
            code = code.replace('NM', str(NM[i]))
            code = code.replace('NREP', str(NREP))

        with open('riccati_mass_spring.py', 'w+') as bench_file:
            bench_file.write(code)

        cmd = 'pmt riccati_mass_spring.py --cgen=True'
        proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)

        try:
            outs, errs = proc.communicate()
        except TimeOutExpired:
            proc.kill()
            print('Exception raised at NM = {}'.format(NM[i]))
            outs, errs = proc.communicate()

        AVG_CPU_TIME.append([float(outs.decode())/NREP, NM[i]])

    if UPDATE_res:
        with open(res_file, 'w+') as res:
            json.dump(AVG_CPU_TIME, res)

else:
    with open(res_file) as res:
        AVG_CPU_TIME = json.load(res)


AVG_CPU_TIME = np.array(AVG_CPU_TIME)

plt.figure()
plt.semilogy(2*AVG_CPU_TIME[:,1], AVG_CPU_TIME[:,0])

if LOAD_BLASFEO_RES:
    with open(blasfeo_res_file) as res:
        AVG_CPU_TIME_BLASFEO = json.load(res)
    AVG_CPU_TIME_BLASFEO = np.array(AVG_CPU_TIME_BLASFEO)
    plt.semilogy(2*AVG_CPU_TIME_BLASFEO[:,1], AVG_CPU_TIME_BLASFEO[:,0], 'o')

plt.legend(['prometeo','BLASFEO API'])
plt.grid()
plt.xlabel('matrix size (nx)')
plt.ylabel('CPU time [s]')
plt.title('Riccati factorization')
if UPDATE_FIGURE:
    plt.savefig(figname + '.pdf', dpi=300, bbox_inches="tight")
plt.show()


