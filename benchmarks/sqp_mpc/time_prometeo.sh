#!/bin/bash
# Time a transpiled SQP example of examples/sqp_mpc: initial solve only
# (n_mpc = 0) and initial solve + 30 RTI steps. Each binary is run 30 times
# and the minimum of its own timer (main without setup) is reported.
# usage: time_prometeo.sh [cartpole | chain [n_free]] [python]
case "$1" in
    chain) EXAMPLE=chain_mpc; NFREE=${2:-3}; shift 2 2>/dev/null || shift ;;
    cartpole) EXAMPLE=sqp_mpc; shift ;;
    *) EXAMPLE=sqp_mpc ;;
esac
PYTHON=${1:-python3}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
WORK=$(mktemp -d)
# BLASFEO_LIB: directory of another libblasfeo.so build (e.g. for another TARGET)
export LD_LIBRARY_PATH=${BLASFEO_LIB:-$ROOT/prometeo/lib/blasfeo}:$ROOT/prometeo/lib/prometeo:$LD_LIBRARY_PATH
for variant in 0 30; do
    d=$WORK/n$variant
    mkdir -p $d
    sed -e "s/^n_mpc : int = 30$/n_mpc : int = $variant/" \
        -e "s/^n_free : dims = 3$/n_free : dims = ${NFREE:-3}/" \
        $ROOT/examples/sqp_mpc/$EXAMPLE.py > $d/$EXAMPLE.py
    (cd $d && $PYTHON -m prometeo $EXAMPLE.py --cgen=True > build.log 2>&1) || { echo "build failed, see $d/build.log"; exit 1; }
    best=1e9
    for r in $(seq 30); do
        t=$(cd $d/__pmt_cache__ && ./$EXAMPLE | grep -oP 'execution time:\K[0-9.]+')
        best=$($PYTHON -c "print(min($best, $t))")
    done
    echo "n_mpc=$variant: $($PYTHON -c "print('%.1f us' % ($best * 1e6))")"
done
rm -rf $WORK
