
publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*

clean:
	rm -rf build dist tkshapes.egg-info

