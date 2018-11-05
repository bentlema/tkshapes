
dist:
	pip install --upgrade pip setuptools twine wheel
	python setup.py sdist bdist_wheel

publish: dist
	twine upload dist/*

clean:
	rm -rf build dist src/tkshapes.egg-info

