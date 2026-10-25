#!/bin/bash
# Time the transpiled SQP example (examples/sqp_mpc): initial solve only
# (n_mpc = 0) and initial solve + 30 RTI steps. Each binary is run 30 times
# and the minimum of its own timer (main without setup) is reported.
# usage: time_prometeo.sh [python]
PYTHON=${1:-python3}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
WORK=$(mktemp -d)
export LD_LIBRARY_PATH=$ROOT/prometeo/lib/blasfeo:$ROOT/prometeo/lib/prometeo:$LD_LIBRARY_PATH
for variant in 0 30; do
    d=$WORK/n$variant
    mkdir -p $d
    sed "s/^n_mpc : int = 30$/n_mpc : int = $variant/" $ROOT/examples/sqp_mpc/sqp_mpc.py > $d/sqp_mpc.py
    (cd $d && $PYTHON -m prometeo sqp_mpc.py --cgen=True > build.log 2>&1) || { echo "build failed, see $d/build.log"; exit 1; }
    best=1e9
    for r in $(seq 30); do
        t=$(cd $d/__pmt_cache__ && ./sqp_mpc | grep -oP 'execution time:\K[0-9.]+')
        best=$($PYTHON -c "print(min($best, $t))")
    done
    echo "n_mpc=$variant: $($PYTHON -c "print('%.1f us' % ($best * 1e6))")"
done
rm -rf $WORK
