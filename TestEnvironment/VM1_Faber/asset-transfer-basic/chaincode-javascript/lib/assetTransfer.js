/*
 * Copyright IBM Corp. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

const { Contract } = require('fabric-contract-api');

class AssetTransfer extends Contract {

    async InitLedger(ctx) {
        const assets = [
            {
                ID: 'asset1',
                FinalConsumer: 'None',
                EnergyKWH: '5',
                Status: 'onchain',
                Owner: 'Tomoko_id',
                AppraisedValue: '300',
            },
            {
                ID: 'asset2',
                FinalConsumer: 'None',
                EnergyKWH: '5',
                Status: 'onchain',
                Owner: 'Brad_id',
                AppraisedValue: '400',
            },
            {
                ID: 'asset3',
                FinalConsumer: 'None',
                EnergyKWH: '10',
                Status: 'onchain',
                Owner: 'JinSoo_id',
                AppraisedValue: '500',
            },
            {
                ID: 'asset4',
                FinalConsumer: 'None',
                EnergyKWH: '10',
                Status: 'onchain',
                Owner: 'Max_id',
                AppraisedValue: '600',
            },
            {
                ID: 'asset5',
                FinalConsumer: 'None',
                EnergyKWH: '15',
                Status: 'onchain',
                Owner: 'Adriana_id',
                AppraisedValue: '700',
            },
            {
                ID: 'asset6',
                FinalConsumer: 'None',
                EnergyKWH: '15',
                Status: 'onchain',
                Owner: 'Michel_id',
                AppraisedValue: '800',
            },
        ];

        for (const asset of assets) {
            asset.docType = 'asset';
            await ctx.stub.putState(asset.ID, Buffer.from(JSON.stringify(asset)));
            console.info(`Asset ${asset.ID} initialized`);
        }
    }

    // CreateAsset issues a new asset to the world state with given details.
    async CreateAsset(ctx, id, finalConsumer, energykwh, status, owner, appraisedValue,docType) {
        const asset = {
            ID: id,
            FinalConsumer: finalConsumer,
            EnergyKWH: energykwh,
            Status: status,
            Owner: owner,
            AppraisedValue: appraisedValue,
            DocType: docType,
        };
        ctx.stub.putState(id, Buffer.from(JSON.stringify(asset)));
        return JSON.stringify(asset);
    }

    // ReadAsset returns the asset stored in the world state with given id.
    async ReadAsset(ctx, id) {
        const assetJSON = await ctx.stub.getState(id); // get the asset from chaincode state
        if (!assetJSON || assetJSON.length === 0) {
            throw new Error(`The asset ${id} does not exist`);
        }
        return assetJSON.toString();
    }

    // UpdateAsset updates an existing asset in the world state with provided parameters.
    async UpdateAsset(ctx, id, finalConsumer, energykwh, status, owner, appraisedValue,docType) {
        const exists = await this.AssetExists(ctx, id);
        if (!exists) {
            throw new Error(`The asset ${id} does not exist`);
        }

        // overwriting original asset with new asset
        const updatedAsset = {
            ID: id,
            FinalConsumer: finalConsumer,
            EnergyKWH: energykwh,
            Status: status,
            Owner: owner,
            AppraisedValue: appraisedValue,
            DocType: docType
        };
        return ctx.stub.putState(id, Buffer.from(JSON.stringify(updatedAsset)));
    }

    // DeleteAsset deletes an given asset from the world state.
    async DeleteAsset(ctx, id) {
        const exists = await this.AssetExists(ctx, id);
        if (!exists) {
            throw new Error(`The asset ${id} does not exist`);
        }
        return ctx.stub.deleteState(id);
    }

    // AssetExists returns true when asset with given ID exists in world state.
    async AssetExists(ctx, id) {
        const assetJSON = await ctx.stub.getState(id);
        return assetJSON && assetJSON.length > 0;
    }

    // TransferAsset updates the owner field of asset with given id in the world state.
    async TransferAsset(ctx, id, newOwner) {
        const assetString = await this.ReadAsset(ctx, id);
        const asset = JSON.parse(assetString);
        asset.Owner = newOwner;
        return ctx.stub.putState(id, Buffer.from(JSON.stringify(asset)));
    }

    // GetAllAssets returns all assets found in the world state.
    async GetAllAssets(ctx) {
        const allResults = [];
        // range query with empty string for startKey and endKey does an open-ended query of all assets in the chaincode namespace.
        const iterator = await ctx.stub.getStateByRange('', '');
        let result = await iterator.next();
        while (!result.done) {
            const strValue = Buffer.from(result.value.value.toString()).toString('utf8');
            let record;
            try {
                record = JSON.parse(strValue);
            } catch (err) {
                console.log(err);
                record = strValue;
            }
            allResults.push({ Key: result.value.key, Record: record });
            result = await iterator.next();
        }
        return JSON.stringify(allResults);
    }

    async GetAllAssetsForOwner(ctx,owner) {
        const allResults = [];
        // range query with empty string for startKey and endKey does an open-ended query of all assets in the chaincode namespace.
        const iterator = await ctx.stub.getStateByRange('', '');
        let result = await iterator.next();
        while (!result.done) {
            const strValue = Buffer.from(result.value.value.toString()).toString('utf8');
            let record;
            try {
                record = JSON.parse(strValue);
            } catch (err) {
                console.log(err);
                record = strValue;
            }
            let obj = JSON.parse(JSON.stringify(record));
            if (obj.Owner==owner) {
               allResults.push({ Key: result.value.key, Record: record });
            }

            //return obj.Owner;
            // console.log(record); // Here, evalutation
            //console.log(typeof record)
            //return record.Result[0].Record.Owner;
            //return record;
            result = await iterator.next();
        }
        return JSON.stringify(allResults);
    }


}

module.exports = AssetTransfer;
