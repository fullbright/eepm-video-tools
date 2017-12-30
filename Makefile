HOST=127.0.0.1
TEST_PATH=./
CODEPATH=./

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} + 

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

pep8:
	pep8 $(CODEPATH)

pep8-full:
	pep8 --show-source --show-pep8 $(CODEPATH)

pep8-stats:
	pep8 --statistics -qq $(CODEPATH)

isort:
	sh -c "isort --skip-glob=.tox --recursive . "

lint:
	flake8 --exclude=.tox

test: clean-pyc
	#py.test --verbose --color=yes $(TEST_PATH)
	nosetests

install-and-test: install test


install:
	virtualenv .venv
	. ./.venv/bin/activate
	pip install -r requirements.txt

docker-run:
	#docker build --file=./Dockerfile --tag=eepm_videos_automator ./
	#docker run --rm --detach=false --name=eepm_video_automator --publish=$(HOST):8080 ubuntu
	#docker run --rm --detach=false --name=eepm_video_automator -v $(PWD):/app  ubuntu /bin/bash
	#docker run --rm -it --name=eepm_video_automator -v /home/sergio/dev/eepm-video-tools:/app -w /app  python:2.7 /bin/bash
	docker run --rm -it --name=eepm_video_automator -v /home/sergio/dev/eepm-video-tools:/app -w /app  python:2.7 make install-and-test
