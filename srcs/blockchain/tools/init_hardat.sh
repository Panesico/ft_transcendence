#!/bin/bash
npm install --legacy-peer-deps hardhat @nomiclabs/hardhat-waffle ethereum-waffle chai @nomiclabs/hardhat-ethers ethers
npm install --legacy-peer-deps hardhat @nomiclabs/hardhat-waffle ethereum-waffle chai @nomiclabs/hardhat-ethers ethers

# Use expect to automate the interactive prompts
expect <<EOF
spawn npx hardhat;
expect "What do you want to do?"
send "Create a JavaScript project\r"
expect "Hardhat project root:"
send "/usr/src/app/blockchain_app\r"
expect "Do you want to add a .gitignore? (Y/n)"
send "y\r"
expect "Do you want to install this sample project's dependencies with npm (hardhat @nomiclabs/hardhat-waffle ethereum-waffle chai @nomiclabs/hardhat-ethers ethers)? (Y/n)"
send "y\r"
expect eof
EOF
#with npm (hardhat @nomiclabs/hardhat-waffle ethereum-waffle chai @nomiclabs/hardhat-ethers ethers)? (Y/n) · y
# ✔ What do you want to do? · Create a basic sample project
# ✔ Hardhat project root: · /path/to/hardhat-docker
# ✔ Do you want to add a .gitignore? (Y/n) · y
# ✔ Do you want to install this sample project's dependencies with npm (hardhat @nomiclabs/hardhat-waffle ethereum-waffle chai @nomiclabs/hardhat-ethers ethers)? (Y/n) · y

# Make sure we initiate git for your IDE.
#git init;

# modify of Hardhat network because of a MetaMask chainId issue:
#cp /tmp/hardat_config.js hardhat.config.local.js;

tail -f /dev/null;