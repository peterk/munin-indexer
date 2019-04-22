FROM node:10.15.3-stretch-slim

# Get key and repo for google chrome stable
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

RUN apt-get update
RUN apt-get install -y git-core build-essential vim python python-pip

# Timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# get fonts for chrome (for screenshots etc
RUN apt-get install -y fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst ttf-freefont --no-install-recommends

RUN npm install -g npm

# Gigantic list of deps to run chromium headless on debian (see https://github.com/GoogleChrome/puppeteer/issues/290#issuecomment-322838700)
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget

# Install regular Chrome as an alternative - add selection in web frontend later?
RUN apt-get install google-chrome-stable -y

RUN mkdir -p /archive
RUN mkdir -p /scripts

# Get squidwarc w puppeteer support
RUN mkdir -p /usr/src/app
RUN mkdir -p /jobs

WORKDIR /usr/src/app

# install squidwarc while we have access to python 2.7
RUN git clone https://github.com/N0taN3rd/Squidwarc.git
WORKDIR Squidwarc

# Temporary fix for node-warc submodule
RUN git submodule deinit -f node-warc
RUN npm install 

RUN git clone https://github.com/N0taN3rd/node-warc.git
WORKDIR node-warc
RUN npm install 

WORKDIR Squidwarc

# get python 3.6.6 (build from source)
ENV LANG C.UTF-8

RUN apt-get install -y --no-install-recommends tk-dev libssl-dev

ENV PYTHON_VERSION 3.6.6

RUN set -ex \
	\
	&& wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
	&& wget -O python.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" \
	&& mkdir -p /usr/src/python \
	&& tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
	&& rm python.tar.xz \
	\
	&& cd /usr/src/python \
	&& gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)" \
	&& ./configure \
		--build="$gnuArch" \
		--enable-loadable-sqlite-extensions \
		--enable-shared \
		--with-system-expat \
		--with-system-ffi \
		--without-ensurepip \
	&& make -j "$(nproc)" \
	&& make install \
	&& ldconfig \
	\
	&& find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' + \
	&& rm -rf /usr/src/python \
	\
	&& python3 --version

# make some useful symlinks that are expected to exist
RUN cd /usr/local/bin \
	&& ln -s idle3 idle \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s python3-config python-config

# if this is called "PIP_VERSION", pip explodes with "ValueError: invalid truth value '<VERSION>'"
ENV PYTHON_PIP_VERSION 19.0

RUN python --version
RUN set -ex; \
	\
	wget -O get-pip.py 'https://bootstrap.pypa.io/get-pip.py'; \
	\
	python get-pip.py \
		--disable-pip-version-check \
		"pip==$PYTHON_PIP_VERSION" \
	; \
	pip --version; \
	\
	find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' +; \
	rm -f get-pip.py

# Continue with rest of archiver app
ADD scripts/* /scripts/
WORKDIR /usr/src/app
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./worker.py worker.py
COPY ./wait-for.sh wait-for.sh
RUN apt-get install -y netcat

CMD ["python", "worker.py"]
