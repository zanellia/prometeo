python3 -m pip install cibuildwheel==1.3.0
python3 -m cibuildwheel --output-dir wheelhouse
python3 -m pip install twine
python3 -m twine upload wheelhouse/*.whl
