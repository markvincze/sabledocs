#!/bin/sh
set -e

SOURCE_DIR=$PWD
TEMP_REPO_DIR=$PWD/../sable-gh-pages

echo "Removing temporary doc directory $TEMP_REPO_DIR"
rm -rf $TEMP_REPO_DIR
mkdir $TEMP_REPO_DIR

echo "Cloning the repo with the gh-pages branch"
git clone https://github.com/markvincze/sabledocs.git --branch gh-pages $TEMP_REPO_DIR

pip install .

cd sample
sabledocs

echo "Clear repo directory"
cd $TEMP_REPO_DIR
git rm -r *

echo "Copy documentation into the repo"
mkdir demo
cp -r $SOURCE_DIR/sample/output/* ./demo
cp $SOURCE_DIR/README.md .

echo "Push the new docs to the remote branch"
git add . -A
git commit -m "Update generated documentation"
git push origin gh-pages

