
build:
	pip install --upgrade pip setuptools twine wheel
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*

clean:
	rm -rf build dist src/tkshapes.egg-info

