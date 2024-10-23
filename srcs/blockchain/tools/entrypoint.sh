#! /bin/sh -l

# Install hardhat dependencies
npm install --save-dev @nomicfoundation/hardhat-toolbox --no-audit
#npm install ethers@latest



# Not sure if this is needed once the contract is already deployed
npx hardhat node
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost