#!/bin/bash

# 需要检查的文件
checkFiles=$(git log --since='date -d "yesterday" +%Y.%m.%d' --name-only --pretty=format:"")
git checkout -- ${checkFiles}

for file in ${checkFiles}; do
    echo $file
    extension="${file##*.}"
    if [ $extension == "txt" ];then
        mv ${file} "bhqz.txt"
    fi

    if [ $extension == "yaml" ];then
        mv ${file} "bhqz.yml"
    fi

done