#!/bin/sh

cd /data
if [ $? -ne 0 ]; then
	echo "Error: the directory /data is not found."
	exit 1
fi

git clone $APP_REPO --single-branch $APP_BRANCH .
if [ $? -ne 0 ]; then
        echo "Error: failed to clone git reposiroty ${APP_REPO}."
        exit 1
fi

# install dependencies (if needed)
pnpm install next@latest react@latest react-dom@latest
if [ $? -ne 0 ]; then
        echo "Error: failed to install npm framework."
        exit 1
fi

pnpm install
if [ $? -ne 0 ]; then
        echo "Error: failed to install npm modules."
        exit 1
fi

# build the app
npm run build
if [ $? -ne 0 ]; then
        echo "Error: failed to build the app."
        exit 1
fi

# run the app
npm run start
if [ $? -ne 0 ]; then
        echo "Error: failed to start the app."
        exit 1
fi
