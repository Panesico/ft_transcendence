#! /bin/sh -l

# sleep 1
# until nc -z -v -w30 authentif 9001 > /dev/null 2>&1; do
#   sleep 1
# done

# Install hardhat dependencies
npm install --save-dev @nomicfoundation/hardhat-toolbox


npx hardhat node