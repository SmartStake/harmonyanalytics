
CREATE TABLE `addressalias` (
  `aliasId` int(10) NOT NULL AUTO_INCREMENT,
  `alias` varchar(45) NOT NULL,
  `address` varchar(128) NOT NULL,
  `lastUpdated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `app` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`aliasId`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=latin1;


CREATE TABLE `auditlog` (
  `auditLogId` int(18) NOT NULL AUTO_INCREMENT,
  `ipAddress` varchar(24) DEFAULT NULL,
  `url` varchar(100) NOT NULL,
  `urlParams` varchar(230) DEFAULT NULL,
  `method` varchar(10) DEFAULT NULL,
  `lastWritten` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `poolId` int(10) DEFAULT NULL,
  `responseTime` int(12) DEFAULT NULL,
  `app` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`auditLogId`),
  KEY `audit_ipaddress` (`ipAddress`,`lastWritten`)
) ENGINE=InnoDB AUTO_INCREMENT=2864195 DEFAULT CHARSET=latin1;


CREATE TABLE `coinstat` (
  `totalStake` float(18,2) NOT NULL,
  `stakingPools` int(11) DEFAULT '20',
  `currentRewardRate` float(5,2) DEFAULT NULL,
  `ssStake` float(18,2) DEFAULT NULL,
  `totalSupply` float(18,0) DEFAULT NULL,
  `circulatingSupply` float(18,0) DEFAULT NULL,
  `symbol` varchar(45) NOT NULL,
  `lastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `btcPrice` float(15,8) DEFAULT NULL,
  `usdPrice` float(12,5) DEFAULT NULL,
  `ssBlocks` int(12) DEFAULT NULL,
  `ssRewards` int(12) DEFAULT NULL,
  `recentBlock` int(12) DEFAULT NULL,
  `blocks_8hrs` int(7) DEFAULT NULL,
  `blocks_24hrs` int(7) DEFAULT NULL,
  `blocks_7days` int(7) DEFAULT NULL,
  `blocks_1hr` int(7) DEFAULT NULL,
  `withdrawSyncTillBlock` int(12) DEFAULT NULL,
  `uniqueDelegates` int(12) DEFAULT NULL,
  `coinId` varchar(45) NOT NULL,
  `totalRewardWithdrawals` float(12,2) DEFAULT NULL,
  `activeAccounts` int(12) DEFAULT NULL,
  `totalPoolStake` int(12) DEFAULT NULL,
  `totalSoloStake` int(12) DEFAULT NULL,
  `percentStaked` float(5,1) DEFAULT NULL,
  `usdStaked` int(12) DEFAULT NULL,
  `usdMcap` int(14) DEFAULT NULL,
  `priceChangeUsd` float(6,2) DEFAULT NULL,
  `rewardsBalance` float(9,3) DEFAULT NULL,
  `blocks_21days` int(10) DEFAULT NULL,
  `actualRewardRate` float(5,2) DEFAULT NULL,
  `blockRate` float(5,2) DEFAULT NULL,
  `medianRawStake` float(18,0) DEFAULT NULL,
  `isSynced` varchar(5) DEFAULT NULL,
  `stakeSupply` float(18,4) DEFAULT NULL,
  `electedPools` int(5) DEFAULT NULL,
  `totalWeightedStake` float(18,2) DEFAULT NULL,
  `otherArr` float(5,2) DEFAULT NULL,
  `epochLastBlock` int(12) DEFAULT NULL,
  `nextEpochTime` int(12) DEFAULT NULL,
  `currentEpoch` int(8) DEFAULT NULL,
  PRIMARY KEY (`coinId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `eventlog` (
  `eventId` int(11) NOT NULL AUTO_INCREMENT,
  `eventName` varchar(45) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `eventTime` int(12) NOT NULL,
  `app` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`eventId`),
  KEY `event_name_time_index` (`eventName`,`eventTime`)
) ENGINE=InnoDB AUTO_INCREMENT=2420473 DEFAULT CHARSET=latin1;



CREATE TABLE `nodehealth` (
  `healthid` int(18) NOT NULL AUTO_INCREMENT,
  `nodeName` varchar(45) NOT NULL,
  `symbol` varchar(45) NOT NULL,
  `checkupTime` timestamp NOT NULL,
  `networkBlockHeight` int(12) NOT NULL,
  `nodeBlockHeight` int(12) NOT NULL,
  `lastBlockValidated` int(12) NOT NULL,
  `lastUpdated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `heightGap` int(12) DEFAULT NULL,
  `poolId` int(5) DEFAULT NULL,
  `shardId` int(11) DEFAULT NULL,
  `epochTimestamp` int(12) DEFAULT NULL,
  PRIMARY KEY (`healthid`)
) ENGINE=InnoDB AUTO_INCREMENT=264826 DEFAULT CHARSET=latin1;

CREATE TABLE `notification` (
  `notificationId` int(11) NOT NULL AUTO_INCREMENT,
  `message` varchar(500) NOT NULL,
  `startDate` timestamp NOT NULL,
  `endDate` timestamp NOT NULL,
  `poolId` int(5) DEFAULT NULL,
  `app` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`notificationId`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;


CREATE TABLE `property` (
  `propertyId` int(12) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `app` varchar(45) NOT NULL,
  `value` varchar(500) DEFAULT NULL,
  `createdOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`propertyId`)
) ENGINE=InnoDB AUTO_INCREMENT=154 DEFAULT CHARSET=latin1;

CREATE TABLE `tgsetting` (
  `tgSettingId` int(11) NOT NULL AUTO_INCREMENT,
  `userId` varchar(25) DEFAULT NULL,
  `chatId` varchar(25) DEFAULT NULL,
  `favPools` varchar(200) DEFAULT NULL,
  `address` varchar(500) DEFAULT NULL,
  `app` varchar(15) DEFAULT NULL,
  `addressAlias` varchar(25) DEFAULT NULL,
  `createdOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `lastUpdated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`tgSettingId`),
  UNIQUE KEY `chatId_app_UNIQUE` (`chatId`,`app`)
) ENGINE=InnoDB AUTO_INCREMENT=200 DEFAULT CHARSET=latin1;

CREATE TABLE `syncstatus` (
  `syncId` int(12) NOT NULL AUTO_INCREMENT,
  `app` varchar(10) DEFAULT NULL,
  `syncType` varchar(45) DEFAULT NULL,
  `syncedTillEpochTime` int(14) DEFAULT NULL,
  `syncedTillBlock` int(12) DEFAULT NULL,
  `lastUpdated` timestamp NULL DEFAULT NULL,
  `syncCategory` varchar(45) DEFAULT NULL,
  `syncedTillEpoch` int(10) DEFAULT NULL,
  PRIMARY KEY (`syncId`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;


CREATE TABLE `haddress` (
  `addressId` int NOT NULL AUTO_INCREMENT,
  `address` varchar(128) NOT NULL,
  `totalStake` double(18,4) DEFAULT '0.0000',
  `addressBalance` double(18,4) DEFAULT '0.0000',
  `totalBalance` double(18,4) DEFAULT '0.0000',
  `lastUpdated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `createdOn` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `alias` varchar(45) DEFAULT NULL,
  `totalRewards` float(15,4) DEFAULT '0.0000',
  `ranking` int DEFAULT NULL,
  `txCount` int DEFAULT '0',
  `firstTxDateTime` timestamp NULL DEFAULT NULL,
  `trackHistory` varchar(5) DEFAULT 'False',
  PRIMARY KEY (`addressId`),
  UNIQUE KEY `haddress_add_unique_index` (`address`),
  KEY `haddress_rank` (`ranking`)
) ENGINE=InnoDB AUTO_INCREMENT=32445 DEFAULT CHARSET=latin1;

CREATE TABLE `hblockrate` (
  `blockRateId` int NOT NULL AUTO_INCREMENT,
  `epochNumber` int DEFAULT NULL,
  `shardId` int DEFAULT NULL,
  `epochStartBlock` int DEFAULT NULL,
  `epochStartTime` int DEFAULT NULL,
  `latestBlock` int DEFAULT NULL,
  `epochLastBlock` int DEFAULT NULL,
  `epochLastBlockTime` int DEFAULT NULL,
  `latestBlockTime` int DEFAULT NULL,
  `epochEnded` tinyint DEFAULT NULL,
  `lastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `blockRate` float(8,5) DEFAULT NULL,
  PRIMARY KEY (`blockRateId`),
  UNIQUE KEY `hbr_shard_epoch` (`epochNumber`,`shardId`),
  KEY `hbr_epoch` (`epochNumber`),
  KEY `hbr_shard` (`shardId`)
) ENGINE=InnoDB AUTO_INCREMENT=249 DEFAULT CHARSET=latin1;

CREATE TABLE `hblskey` (
  `blsKeyId` int NOT NULL AUTO_INCREMENT,
  `blsKey` varchar(100) NOT NULL,
  `shardId` int NOT NULL,
  `creationDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `hPoolId` int NOT NULL,
  `nodeVersion` varchar(45) DEFAULT NULL,
  `lastUpdated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`blsKeyId`),
  KEY `hblskey_uk` (`blsKey`)
) ENGINE=InnoDB AUTO_INCREMENT=1874 DEFAULT CHARSET=latin1;

CREATE TABLE `hevent` (
  `eventId` int NOT NULL AUTO_INCREMENT,
  `eventType` varchar(45) NOT NULL,
  `epochNumber` int DEFAULT NULL,
  `blockNumber` int DEFAULT NULL,
  `epochBlockTime` int DEFAULT NULL,
  `txHash` varchar(128) DEFAULT NULL,
  `address` varchar(128) DEFAULT NULL,
  `hPoolId` int DEFAULT NULL,
  `amount` float(14,4) DEFAULT NULL,
  `lastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `otherAddress` varchar(128) DEFAULT NULL,
  `notifiedInd` tinyint DEFAULT '0',
  PRIMARY KEY (`eventId`),
  KEY `hevent_pool_index` (`hPoolId`),
  KEY `hevent_address_index` (`address`),
  KEY `hevent_eventtype_bl_index` (`eventType`,`blockNumber`),
  KEY `hevent_epoch` (`epochNumber`,`hPoolId`),
  KEY `hevent_notified` (`notifiedInd`),
  KEY `hevent_pool_block_index` (`blockNumber`,`hPoolId`),
  KEY `hevent_add_type_time` (`epochBlockTime`,`eventType`,`address`)
) ENGINE=InnoDB AUTO_INCREMENT=178374 DEFAULT CHARSET=latin1;

CREATE TABLE `hhistory` (
  `historyId` int NOT NULL AUTO_INCREMENT,
  `epoch` int DEFAULT NULL,
  `dataType` varchar(10) DEFAULT NULL,
  `poolId` int DEFAULT NULL,
  `keyObject` varchar(25) DEFAULT NULL,
  `address` varchar(70) DEFAULT NULL,
  `value1` float(18,4) DEFAULT NULL,
  `createdOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `lastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `value2` float(18,4) DEFAULT NULL,
  `value3` float(18,4) DEFAULT NULL,
  `value4` float(18,4) DEFAULT NULL,
  `value5` float(18,4) DEFAULT NULL,
  `value6` float(18,4) DEFAULT NULL,
  `value7` float(18,4) DEFAULT NULL,
  `value8` float(18,4) DEFAULT NULL,
  `value9` float(18,4) DEFAULT NULL,
  PRIMARY KEY (`historyId`),
  KEY `hh_epoch_dt_pool` (`epoch`,`poolId`,`dataType`),
  KEY `hh_address` (`address`,`dataType`)
) ENGINE=InnoDB AUTO_INCREMENT=527730 DEFAULT CHARSET=latin1;

CREATE TABLE `hkeyperf` (
  `keyPerfId` int NOT NULL AUTO_INCREMENT,
  `blsKey` varchar(100) NOT NULL,
  `epochNumber` int NOT NULL,
  `syncTime` int NOT NULL,
  `effectiveStake` int NOT NULL,
  `rawStake` int NOT NULL,
  `groupPercentStake` float(10,7) DEFAULT NULL,
  `overallPercentStake` float(10,7) DEFAULT NULL,
  `groupPercentReward` float(10,7) DEFAULT NULL,
  `overallPercentReward` float(10,7) DEFAULT NULL,
  `reward` float(14,4) DEFAULT NULL,
  `isBadPerf` varchar(5) DEFAULT 'False',
  `groupRewardRatio` float(6,3) DEFAULT NULL,
  `keyPerfIndex` float(6,3) DEFAULT NULL,
  PRIMARY KEY (`keyPerfId`),
  KEY `hkeyperf_epoch_time` (`blsKey`,`epochNumber`,`syncTime`)
) ENGINE=InnoDB AUTO_INCREMENT=4161150 DEFAULT CHARSET=latin1;

CREATE TABLE `hnotification` (
  `notificationId` int NOT NULL AUTO_INCREMENT,
  `notificationType` varchar(25) NOT NULL,
  `address` varchar(100) DEFAULT NULL,
  `hPoolId` int DEFAULT NULL,
  `epochNumber` int DEFAULT NULL,
  `value1` float(13,4) DEFAULT NULL,
  `value2` float(13,4) DEFAULT NULL,
  `notifiedInd` tinyint NOT NULL DEFAULT '0',
  `watchInd` tinyint NOT NULL DEFAULT '0',
  `creationDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `blsKey` varchar(100) DEFAULT NULL,
  `blockNumber` int DEFAULT NULL,
  `otherData1` varchar(45) DEFAULT NULL,
  `otherData2` varchar(45) DEFAULT NULL,
  `txHash` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`notificationId`),
  KEY `hn_epoch_pool` (`hPoolId`,`notificationType`,`epochNumber`,`blsKey`)
) ENGINE=InnoDB AUTO_INCREMENT=8336 DEFAULT CHARSET=latin1;

CREATE TABLE `hpool` (
  `hPoolId` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `identity` varchar(65) DEFAULT NULL,
  `securitycontact` varchar(65) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `address` varchar(128) NOT NULL,
  `details` varchar(500) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `blsKeyCount` int DEFAULT NULL,
  `minSelfDelegation` float(14,2) DEFAULT NULL,
  `maxTotalDelegation` float(18,2) DEFAULT NULL,
  `totalRewards` float(14,2) DEFAULT NULL,
  `createdDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `lastUpdated` timestamp NOT NULL,
  `website` varchar(128) DEFAULT NULL,
  `lifetimeToSign` int DEFAULT NULL,
  `lifetimeApr` float(12,2) DEFAULT NULL,
  `currentEpochSigned` int DEFAULT NULL,
  `currentEpochToSign` int DEFAULT NULL,
  `currentEpochSignPer` float(8,2) DEFAULT NULL,
  `uniqueDelegates` int DEFAULT NULL,
  `fee` float(8,4) DEFAULT NULL,
  `maxFee` float(8,4) DEFAULT NULL,
  `feeChangeRate` float(8,4) DEFAULT NULL,
  `creationBlock` int DEFAULT NULL,
  `lastUpdateBlock` int DEFAULT NULL,
  `totalStaked` float(14,2) DEFAULT NULL,
  `elected` varchar(20) DEFAULT NULL,
  `booted` varchar(20) DEFAULT NULL,
  `optimalBlsKeyCount` int DEFAULT NULL,
  `selfStake` float(14,2) DEFAULT NULL,
  `status` varchar(45) DEFAULT NULL,
  `syncEpochTime` int DEFAULT NULL,
  `bidPerSeat` float(18,0) DEFAULT NULL,
  `lifetimeSigned` int DEFAULT NULL,
  `currentEpochRewards` float(14,2) DEFAULT NULL,
  `currentApr` float(6,2) DEFAULT NULL,
  `currentNetApr` float(6,2) DEFAULT NULL,
  `avgApr` float(6,2) DEFAULT NULL,
  `avgNetApr` float(6,2) DEFAULT NULL,
  `prevEpochApr` float(6,2) DEFAULT NULL,
  `prevEpochNetApr` float(6,2) DEFAULT NULL,
  `avgEri` float(6,2) DEFAULT NULL,
  `prevEpochEri` float(6,2) DEFAULT NULL,
  `currentEri` float(6,2) DEFAULT NULL,
  `activeStatus` varchar(10) DEFAULT NULL,
  `feeChangedEpoch` int DEFAULT NULL,
  `feeChangedDesc` varchar(45) DEFAULT NULL,
  `keepName` varchar(5) DEFAULT 'False',
  `prevFee` float(8,4) DEFAULT NULL,
  `avgSignPer` decimal(5,2) DEFAULT NULL,
  `avgSigned` int DEFAULT NULL,
  `avgToSign` int DEFAULT NULL,
  `electionRate` decimal(5,2) DEFAULT NULL,
  `isPva` varchar(5) DEFAULT 'False',
  `isEverElected` varchar(5) DEFAULT 'False',
  `stakeWeight` float(6,3) DEFAULT NULL,
  PRIMARY KEY (`hPoolId`),
  KEY `hp_address_idx` (`address`),
  KEY `hp_status_idx` (`status`),
  KEY `hp_feeChangedEpoch_idx` (`feeChangedEpoch`),
  KEY `hp_isEverElected_idx` (`isEverElected`)
) ENGINE=InnoDB AUTO_INCREMENT=370 DEFAULT CHARSET=latin1;

CREATE TABLE `hpooldel` (
  `poolDelId` int NOT NULL AUTO_INCREMENT,
  `hPoolId` int NOT NULL,
  `address` varchar(128) DEFAULT NULL,
  `stake` float(14,4) DEFAULT NULL,
  `reward` float(12,4) DEFAULT NULL,
  `lastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `createdOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`poolDelId`),
  KEY `pooldel_pool_add_index` (`hPoolId`,`address`),
  KEY `pd_pool_add_stake_reward_index` (`hPoolId`,`address`,`stake`,`reward`)
) ENGINE=InnoDB AUTO_INCREMENT=656308 DEFAULT CHARSET=latin1;

CREATE TABLE `hpooldelhistory` (
  `poolDelId` int NOT NULL AUTO_INCREMENT,
  `hPoolId` int NOT NULL,
  `address` varchar(128) DEFAULT NULL,
  `stake` float(14,4) DEFAULT NULL,
  `reward` float(12,4) DEFAULT NULL,
  `lastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `createdOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `syncTime` timestamp NULL DEFAULT NULL,
  `epochNumber` int DEFAULT NULL,
  PRIMARY KEY (`poolDelId`),
  KEY `hpdh_pool_add_time_index` (`hPoolId`,`address`,`syncTime`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `hpoolperf` (
  `hPoolPerfId` int NOT NULL AUTO_INCREMENT,
  `hPoolId` int NOT NULL,
  `epochNumber` int DEFAULT NULL,
  `mode` varchar(10) DEFAULT NULL,
  `blsKeyCount` int DEFAULT NULL,
  `syncTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `syncEpochTime` int DEFAULT NULL,
  `createdDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `signed` int DEFAULT NULL,
  `askedToSign` int DEFAULT NULL,
  `signPer` float(6,2) DEFAULT NULL,
  `uniqueDelegates` int DEFAULT NULL,
  `totalStaked` float(14,2) DEFAULT NULL,
  `elected` varchar(20) DEFAULT NULL,
  `booted` varchar(20) DEFAULT NULL,
  `selfStake` float(14,2) DEFAULT NULL,
  `status` varchar(45) DEFAULT NULL,
  `bidPerSeat` float(18,0) DEFAULT NULL,
  `fee` float(6,4) DEFAULT NULL,
  `lifetimeSigned` int DEFAULT NULL,
  `lifetimeToSign` int DEFAULT NULL,
  `lifetimeRewards` float(14,2) DEFAULT NULL,
  `rewards` float(14,2) DEFAULT NULL,
  `apr` float(6,2) DEFAULT NULL,
  `netApr` float(6,2) DEFAULT NULL,
  `eri` float(8,2) DEFAULT NULL,
  PRIMARY KEY (`hPoolPerfId`),
  KEY `in_hpp_mode_epoch_elected` (`epochNumber`,`mode`,`elected`),
  KEY `in_hpp_mode_synctime_idx` (`mode`,`syncTime`),
  KEY `in_hpp_mode_pool_time` (`hPoolId`,`mode`,`syncTime`)
) ENGINE=InnoDB AUTO_INCREMENT=1608748 DEFAULT CHARSET=latin1;

CREATE TABLE `hsharddelay` (
  `shardDelayId` int NOT NULL AUTO_INCREMENT,
  `epochNumber` int NOT NULL,
  `shardId` int NOT NULL,
  `blockNumber` int NOT NULL,
  `crossLinkDelay` int DEFAULT NULL,
  `crossLinkBlock` int DEFAULT NULL,
  `isDelayedInd` varchar(5) NOT NULL DEFAULT 'False',
  `slots` int DEFAULT NULL,
  `syncTime` int DEFAULT NULL,
  PRIMARY KEY (`shardDelayId`),
  KEY `hshard_sync` (`syncTime`)
) ENGINE=InnoDB AUTO_INCREMENT=27385 DEFAULT CHARSET=latin1;

CREATE TABLE `htransaction` (
  `txId` int NOT NULL AUTO_INCREMENT,
  `txHash` varchar(68) NOT NULL,
  `fromAddress` varchar(45) DEFAULT NULL,
  `toAddress` varchar(45) DEFAULT NULL,
  `txType` varchar(15) DEFAULT NULL,
  `amount` float(18,4) DEFAULT NULL,
  `epochTimestamp` int DEFAULT NULL,
  `blockNumber` int DEFAULT NULL,
  `txDate` date DEFAULT NULL,
  `epoch` int DEFAULT NULL,
  `shardId` int DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  `txFee` float(10,7) DEFAULT NULL,
  `nonce` int DEFAULT NULL,
  `token` varchar(10) DEFAULT NULL,
  `isStakingTx` tinyint DEFAULT NULL,
  `hPoolId` int DEFAULT NULL,
  `toShardId` int DEFAULT NULL,
  `txIndex` int DEFAULT NULL,
  PRIMARY KEY (`txId`),
  KEY `htx_txhash` (`txHash`),
  KEY `htx_address` (`fromAddress`,`toAddress`),
  KEY `htx_epochtime` (`epochTimestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=7978 DEFAULT CHARSET=latin1;

CREATE TABLE `htxsummary` (
  `summaryId` int NOT NULL AUTO_INCREMENT,
  `txDate` date NOT NULL,
  `txCategory` varchar(10) NOT NULL,
  `txCount` int DEFAULT NULL,
  `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `lastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `shardId` int DEFAULT NULL,
  PRIMARY KEY (`summaryId`),
  KEY `txsum_date_type` (`txDate`,`txCategory`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1;


INSERT INTO `coinstat` (`totalStake`,`stakingPools`,`currentRewardRate`,`ssStake`,`totalSupply`,`circulatingSupply`,`symbol`,`lastUpdated`,`btcPrice`,`usdPrice`,`ssBlocks`,`ssRewards`,`recentBlock`,`blocks_8hrs`,`blocks_24hrs`,`blocks_7days`,`blocks_1hr`,`withdrawSyncTillBlock`,`uniqueDelegates`,`coinId`,`totalRewardWithdrawals`,`activeAccounts`,`totalPoolStake`,`totalSoloStake`,`percentStaked`,`usdStaked`,`usdMcap`,`priceChangeUsd`,`rewardsBalance`,`blocks_21days`,`actualRewardRate`,`blockRate`,`medianRawStake`,`isSynced`,`stakeSupply`,`electedPools`,`totalWeightedStake`,`otherArr`,`epochLastBlock`,`nextEpochTime`,`currentEpoch`) VALUES (3856964608.00,292,11.43,NULL,12600000512,6963899392,'HARMONY','2020-08-29 02:18:22',0.00000094,0.01075,NULL,NULL,4601624,NULL,NULL,NULL,NULL,NULL,1820,'4',NULL,NULL,NULL,NULL,55.4,41471132,66758296,-2.16,NULL,NULL,NULL,NULL,5827559,NULL,NULL,NULL,NULL,NULL,4603902,1598678879,260);
INSERT INTO `syncstatus` (`app`,`syncType`,`syncedTillEpochTime`,`syncedTillBlock`,`lastUpdated`,`syncCategory`,`syncedTillEpoch`) VALUES ('HARMONY','AddressHistory',NULL,NULL,'2020-08-28 06:51:23','History',260);
INSERT INTO `eventlog` (`eventName`,`description`,`eventTime`,`app`) VALUES ('harmonyLastSyncedEventBlockHeight','3341867',1493122425,'HARMONY');
