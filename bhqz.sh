#!/bin/bash

ShellDir=${JD_DIR:-$(
    cd $(dirname $0)
    pwd
)}

git clone https://github.com/bhqz/bhqz.git bhqz
cd bhqz
# 需要检查的文件
checkFiles=$(git log --since='date -d "yesterday" +%Y.%m.%d' --name-only --pretty=format:"")
git checkout -- ${checkFiles}
echo "bhqz path"
pwd
echo "checkout files"
ls ss
for file in ${checkFiles}; do
    echo $file
    extension="${file##*.}"
    if [ $extension == "txt" ];then
        mv ${ShellDir}/bhqz/${file} ${ShellDir}/bhqz.txt
    fi

    if [ $extension == "yaml" ];then
        mv ${ShellDir}/bhqz/${file} ${ShellDir}/bhqz.yml
    fi
done
cd ${ShellDir} && rm -rf bhqz