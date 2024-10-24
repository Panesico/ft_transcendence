const hre = require("hardhat");
const fs = require('fs');
const path = './deployedAddress.json';

async function main() {
  const Contract = await hre.ethers.deployContract("TournamentManager", []);

  await Contract.waitForDeployment();

  contractAddress = await Contract.getAddress();

  console.log(`Contract deployed to ${await Contract.getAddress()}`);
  fs.writeFileSync(path, JSON.stringify({ contractAddress: contractAddress }));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

// const hre = require("hardhat");
// const fs = require('fs');

// const path = './deployedAddress.json';

// async function main() {
//   let contractAddress;
//   if (fs.existsSync(path)) {
//     // if we already deployed the contract, read the address
//     const rawdata = fs.readFileSync(path);
//     const data = JSON.parse(rawdata);
//     contractAddress = data.contractAddress;
//     console.log(`Contract already deployed to ${contractAddress}`);
//   }
//   else
//   {
//     // Deploy the conytract and save the address
//     const Contract = await hre.ethers.deployContract("TournamentManager", []);
//     await Contract.waitForDeployment();

//     console.log(`Contract deployed to ${await Contract.getAddress()}`);
//     contractAddress = await Contract.getAddress();

//     fs.writeFileSync(path, JSON.stringify({ contractAddress: contractAddress }));
//   }
// }

// main().catch((error) => {
//   console.error(error);
//   process.exitCode = 1;
// });