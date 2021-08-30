#!/bin/bash

# 需要检查的文件
checkFiles=$(git diff --name-only HEAD~ HEAD | grep -v zip)
git checkout -- ${checkFiles}

for file in ${checkFiles}; do
    extension="${file##*.}"
    if [ $extension == "txt" ];then
        mv ${file} "v2.txt"
    fi

    if [ $extension == "yml" ];then
        mv ${file} "clash.yml"
    fi

done