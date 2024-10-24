#! /bin/sh -l

# Install hardhat dependencies
npm install --save-dev hardhat --no-audit
npm install --save-dev @nomicfoundation/hardhat-toolbox --no-audit
#npm install ethers@latest

# Start the hardhat node in the background
npx hardhat node &

# Wait for the node to be ready
sleep 10

# Compile and deploy the contract only if it is not already deployed
if [ ! -f "./deployedAddress.json" ]; then
    echo "Deploying contract"
    npx hardhat compile
    npx hardhat run scripts/deploy.js --network localhost
fi

# Keep the script running to maintain the node
wait