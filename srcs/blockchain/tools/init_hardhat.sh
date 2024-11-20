#! /bin/sh -l
# Install hardhat dependencies
echo "Installing npm"
npm install -g npm@10.9.0

echo "Installing hardhat dependencies"
npm install --save-dev hardhat --no-audit

echo "Installing hardhat plugins"
npm install --save-dev @nomicfoundation/hardhat-toolbox --no-audit

# Start the hardhat node in the background
nohup npx hardhat node > /dev/null 2>&1 &
nohup bash -c 'while true; do sleep 1; done' &

# Wait for the node to be ready
sleep 10

# Compile and deploy the contract
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost

sleep 5

ps aux | grep '[n]ode' | awk '{print $2}' | while read pid; do
    # Kill the process by its PID
    kill -9 $pid
done

nohup npx hardhat node &
# Wait for the node to be ready
sleep 10
# Compile and deploy the contract
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost

# Keep the script running to maintain the node
wait