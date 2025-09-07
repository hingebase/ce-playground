for x in "$CONDA_PREFIX"/etc/conda/activate.d/*.sh; do
    . $x
done
"$CONDA_PREFIX/Library/bin/gojq.exe" -cn '$ENV'
