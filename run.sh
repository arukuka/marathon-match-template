#!/bin/sh

mkdir -p ./tools/out

for i in $(seq 0 99)
do
    filename="$(printf '%04d.txt' "${i}")"
    input="./tools/in/${filename}"
    output="./tools/out/${filename}"
    ./build/main < "${input}" > "${output}" 2>/dev/null
    printf "[%04d] " "${i}"
    ./tools/target/release/vis "${input}" "${output}"
done
