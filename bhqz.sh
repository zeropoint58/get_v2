#!/bin/bash
shopt -s extglob

ShellDir=${JD_DIR:-$(
    cd $(dirname $0)
    pwd
)}

git clone https://github.com/bhqz/bhqz.git bhqz
cd bhqz
rm -rf !(.git)
# 需要检查的文件
checkFiles=$(git log --since='date -d "yesterday" +%Y.%m.%d' --name-only --pretty=format:"")
git checkout -- ${checkFiles}
cd ss/12
pwd
ls
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
echo "mv successed"
cd ${ShellDir} && rm -rf bhqz