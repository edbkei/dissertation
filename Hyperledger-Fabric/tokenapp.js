/*
 * Copyright IBM Corp. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

                // ------------------------------------------------------------------------------------------------------------------------------------------------------//
                // command line: node tokenapp.js arg1 arg2 arg3 arg4 arg5 arg6 arg7 arg8                                                                                //
                // ------------------------------------------------------------------------------------------------------------------------------------------------------//
                //  arg1      arg2           arg3               arg4             Description                                                                             //
                //            arg5           arg6               arg7                                                                                                     //
                // ------------------------------------------------------------------------------------------------------------------------------------------------------//
                //  init                                                         provide initial list of tokens in the ledger                                            //
                //  all                                                          List of tokens from ledger.                                                             //
                //  read      <token>                                            List specific asset token.                                                              //
                //  create    <token>        <InstallationID>  <EnergyKWH>       Create one asset. Token ID, installation ID, energy (KWH)                               //
                //            <Ts>           <Owner>           <AppraisedValue>  Timestamp, Owner, Appraised value.                                                      //
                //  delete    <token>                                            Delete asset token.                                                                     //
                //  transfer  <token>        <to>                                Transfer token <asset> to <to>.                                                         //
                //  exists    <token>                                            Check if <token> exists                                                                 //
                //  update    <token>        <InstallationID>  <EnergyKWH>       Update asset token. Token ID, installation ID, energy (KWH)                             //
                //            <Ts>           <Owner>           <AppraisedValue>  Timestamp, Owner, Appraised value                                                     //
                // ------------------------------------------------------------------------------------------------------------------------------------------------------//
                //  Examples:                                                                      Results:                                            Fabric            //
                //                                                                                 -- CRUD --                                          Interface         //
                //  node tokenapp.js create assetx 123123123 10 2021-01-01T14:16:17 Tom 1300       assetx token with its attributes, created.          CreateAllAssets   //
                //  node tokenapp.js read assetx                                                   assetx token attributes, read.                      ReadAsset         //
                //  node tokenapp.js update assetx 123123123 10 2021-01-01T14:16:17 Tom 1300       assetx token attributes, updated.                   UpdateAsset       //
                //  node tokenapp.js delete assetx                                                 assetx token, deleted.                              DeleteAsset       //
                //                                                                                 -- OTHERS --                                                          //
                //  node tokenapp.js all                                                           all tokens, listed.                                 GetAllAssets      //
                //  node tokenapp.js exists assetx                                                 True/False. About token assetx existance.           AssetExists       //
                //  node tokenapp.js init                                                          Initiate Ledger with a predefined list of tokens.   InitLedger        //
                //  node tokenapp.js transfer assetx OwnerB                                        assetx token is transfered from Owner to OwnerB.    TransferAsset     //
                // ------------------------------------------------------------------------------------------------------------------------------------------------------//
                //                                                                                                                                                       //
                // IMPORTANT:                                                                                                                                            //
                // 1- First command of token application is: node tokenapp.js init. Read Preconditions in item 2.                                                        //
                // 2- Preconditions: According to instruction: https://hyperledger-fabric.readthedocs.io/en/release-2.2/write_first_app.html                             //
                //    Issue commands as follow:                                                                                                                          //
                //                             cd ~fabric-samples/test-network                                                                                           //
                //                             ./network.sh down                                                                                                         //
                //                             docker ps -a                                                                                                              //
                //                             ./network.sh up createChannel -c mychannel -ca                                                                            //
                //                             ./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic2/chaincode-javascript/ -ccl javascript                      //
                //    In another terminal do:                                                                                                                            //
                //                             cd ~asset-transfer-basic2/application-javascript                                                                          //
                //                             npm install                                                                                                               //
                //                             node tokenapp.js arg1 arg2 arg3 arg4 arg5 arg6 arg7 arg8                                                                  //
                // 3- To shutdown token application, do:                                                                                                                 //
                //                             cd ~fabric-samples/test-network                                                                                           //
                //                             ./network.sh down                                                                                                         //
                //                             docker ps -a                                                                                                              //
                // ------------------------------------------------------------------------------------------------------------------------------------------------------//

'use strict';

const { Gateway, Wallets } = require('fabric-network');
const FabricCAServices = require('fabric-ca-client');
const path = require('path');
const { buildCAClient, registerAndEnrollUser, enrollAdmin } = require('../../test-application/javascript/CAUtil.js');
const { buildCCPOrg1, buildWallet } = require('../../test-application/javascript/AppUtil.js');

const channelName = 'mychannel';
const chaincodeName = 'basic';
const mspOrg1 = 'Org1MSP';
const walletPath = path.join(__dirname, 'wallet');
const org1UserId = 'appUser';

function prettyJSONString(inputString) {
	return JSON.stringify(JSON.parse(inputString), null, 2);
}

// pre-requisites:
// - fabric-sample two organization test-network setup with two peers, ordering service,
//   and 2 certificate authorities
//         ===> from directory /fabric-samples/test-network
//         ./network.sh up createChannel -ca
// - Use any of the asset-transfer-basic chaincodes deployed on the channel "mychannel"
//   with the chaincode name of "basic". The following deploy command will package,
//   install, approve, and commit the javascript chaincode, all the actions it takes
//   to deploy a chaincode to a channel.
//         ===> from directory /fabric-samples/test-network
//         ./network.sh deployCC -ccn basic -ccl javascript
// - Be sure that node.js is installed
//         ===> from directory /fabric-samples/asset-transfer-basic/application-javascript
//         node -v
// - npm installed code dependencies
//         ===> from directory /fabric-samples/asset-transfer-basic/application-javascript
//         npm install
// - to run this test application
//         ===> from directory /fabric-samples/asset-transfer-basic/application-javascript
//         node app.js

// NOTE: If you see  kind an error like these:
/*
    2020-08-07T20:23:17.590Z - error: [DiscoveryService]: send[mychannel] - Channel:mychannel received discovery error:access denied
    ******** FAILED to run the application: Error: DiscoveryService: mychannel error: access denied

   OR

   Failed to register user : Error: fabric-ca request register failed with errors [[ { code: 20, message: 'Authentication failure' } ]]
   ******** FAILED to run the application: Error: Identity not found in wallet: appUser
*/
// Delete the /fabric-samples/asset-transfer-basic/application-javascript/wallet directory
// and retry this application.
//
// The certificate authority must have been restarted and the saved certificates for the
// admin and application user are not valid. Deleting the wallet store will force these to be reset
// with the new certificate authority.
//

/**
 *  A test application to show basic queries operations with any of the asset-transfer-basic chaincodes
 *   -- How to submit a transaction
 *   -- How to query and check the results
 *
 * To see the SDK workings, try setting the logging to show on the console before running
 *        export HFC_LOGGING='{"debug":"console"}'
 */
async function main() {
        var args = process.argv.slice(2);
        console.log('Arguments: ', args);
        //console.log('args: ', args); 
        //console.log('args[0]: ', args[0]);
        //console.log('args[1]: ', args[1]);

	try {
		// build an in memory object with the network configuration (also known as a connection profile)
		const ccp = buildCCPOrg1();

		// build an instance of the fabric ca services client based on
		// the information in the network configuration
		const caClient = buildCAClient(FabricCAServices, ccp, 'ca.org1.example.com');

		// setup the wallet to hold the credentials of the application user
		const wallet = await buildWallet(Wallets, walletPath);

		// in a real application this would be done on an administrative flow, and only once
		await enrollAdmin(caClient, wallet, mspOrg1);

		// in a real application this would be done only when a new user was required to be added
		// and would be part of an administrative flow
		await registerAndEnrollUser(caClient, wallet, mspOrg1, org1UserId, 'org1.department1');

		// Create a new gateway instance for interacting with the fabric network.
		// In a real application this would be done as the backend server session is setup for
		// a user that has been verified.


		const gateway = new Gateway();

		try {
			// setup the gateway instance
			// The user will now be able to create connections to the fabric network and be able to
			// submit transactions and query. All transactions submitted by this gateway will be
			// signed by this user using the credentials stored in the wallet.
			await gateway.connect(ccp, {
				wallet,
				identity: org1UserId,
				discovery: { enabled: true, asLocalhost: true } // using asLocalhost as this gateway is using a fabric network deployed locally
			});

			// Build a network instance based on the channel where the smart contract is deployed
			const network = await gateway.getNetwork(channelName);

			// Get the contract from the network.
			const contract = network.getContract(chaincodeName);

                        if (args[0] === 'init') {
			    // Initialize a set of asset data on the channel using the chaincode 'InitLedger' function.
			    // This type of transaction would only be run once by an application the first time it was started after it
			    // deployed the first time. Any updates to the chaincode deployed later would likely not need to run
			    // an "init" type function.
			   console.log('\n--> Submit Transaction: InitLedger, function creates the initial set of assets on the ledger');
			   await contract.submitTransaction('InitLedger');
			   console.log('*** Result: committed'); 

			   // Let's try a query type operation (function).
		           // This will be sent to just one peer and the results will be shown.
			   console.log('\n--> Evaluate Transaction: GetAllAssets, function returns all the current assets on the ledger');
			   let result = await contract.evaluateTransaction('GetAllAssets');
			   console.log(`*** Result: ${prettyJSONString(result.toString())}`);
 
                        } else if (args[0] === 'all') {
			          // Let's try a query type operation (function).
			          // This will be sent to just one peer and the results will be shown.
			         console.log('\n--> Evaluate Transaction: GetAllAssets, function returns all the current assets on the ledger');
			         let result = await contract.evaluateTransaction('GetAllAssets');
			         console.log(`*** Result: ${prettyJSONString(result.toString())}`);
                        } else if (args[0] === 'read') {
   			          console.log('\n--> Evaluate Transaction: ReadAsset, function returns args attributes');
			          let result = await contract.evaluateTransaction('ReadAsset', args[1]);
			          console.log(`*** Result: ${prettyJSONString(result.toString())}`);
                        } else if (args[0] === 'delete') {
   			          console.log('\n--> Evaluate Transaction: ReadAsset, function returns args attributes');
			          let result = await contract.evaluateTransaction('DeleteAsset', args[1]);
			          console.log(`*** Result: ${prettyJSONString(result.toString())}`);
                        } else if (args[0] === 'transfer') {
			          console.log('\n--> Submit Transaction: TransferAsset asset from A to B');
			          await contract.submitTransaction('TransferAsset', args[1], args[2]);
			          console.log('*** Result: committed');
                        } else if (args[0] == 'exists') {        
			          console.log('\n--> Evaluate Transaction: AssetExists, function returns "true" if an asset with given assetID exist');
			          let result = await contract.evaluateTransaction('AssetExists', args[1]);
			          console.log(`*** Result: ${prettyJSONString(result.toString())}`);
                        } else if (args[0] == 'create') {        
			          // This will be sent to both peers and if both peers endorse the transaction, the endorsed proposal will be sent
			          // to the orderer to be committed by each of the peer's to the channel ledger.
			          console.log('\n--> Submit Transaction: CreateAsset, creates new asset with ID, InstallationID, EnergyKWH, Ts, Owner, and appraisedValue arguments');
			          await contract.submitTransaction('CreateAsset', args[1], args[2], parseInt(args[3]),args[4], args[5], parseInt(args[6]));
			          console.log('*** Result: committed');
                        } else if (args[0] === 'update') {
			          console.log('\n--> Submit Transaction: UpdateAsset asset1, change the appraisedValue to 350');
			          await contract.submitTransaction('UpdateAsset', args[1], args[2], parseInt(args[3]),args[4], args[5], parseInt(args[6]));
			          console.log('*** Result: committed');
                        }

                        else {
                             console.log('Wrong parameter.');

                        }

 
		} finally {
			// Disconnect from the gateway when the application is closing
			// This will close all connections to the network
			gateway.disconnect();
		}
	} catch (error) {
		console.error(`******** FAILED to run the application: ${error}`);
	}
}

main();
