
build:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*

clean:
	rm -rf build dist src/tkshapes.egg-info

