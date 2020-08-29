
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


CREATE TABLE `haddress` (
  `addressId` int(11) NOT NULL AUTO_INCREMENT,
  `address` varchar(128) NOT NULL,
  `totalStake` double(18,4) DEFAULT '0.0000',
  `addressBalance` double(18,4) DEFAULT '0.0000',
  `totalBalance` double(18,4) DEFAULT '0.0000',
  `lastUpdated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `createdOn` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `alias` varchar(45) DEFAULT NULL,
  `totalRewards` float(15,4) DEFAULT '0.0000',
  `rank` int(11) DEFAULT NULL,
  `txCount` int(10) DEFAULT '0',
  `firstTxDateTime` timestamp NULL DEFAULT NULL,
  `trackHistory` varchar(5) DEFAULT 'False',
  PRIMARY KEY (`addressId`),
  KEY `haddress_address_idx` (`address`),
  KEY `haddress_balance_idx` (`totalBalance`)
) ENGINE=InnoDB AUTO_INCREMENT=92918 DEFAULT CHARSET=latin1;

CREATE TABLE `hevent` (
  `eventId` int(12) NOT NULL AUTO_INCREMENT,
  `eventType` varchar(45) NOT NULL,
  `epochNumber` int(6) DEFAULT NULL,
  `blockNumber` int(12) DEFAULT NULL,
  `epochBlockTime` int(12) DEFAULT NULL,
  `txHash` varchar(128) DEFAULT NULL,
  `address` varchar(128) DEFAULT NULL,
  `hPoolId` int(6) DEFAULT NULL,
  `amount` float(14,4) DEFAULT NULL,
  `lastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `otherAddress` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`eventId`),
  KEY `hevent_pool_index` (`hPoolId`),
  KEY `hevent_address_index` (`address`),
  KEY `hevent_eventtype_bl_index` (`eventType`,`blockNumber`),
  KEY `hevent_epoch` (`epochNumber`,`hPoolId`)
) ENGINE=InnoDB AUTO_INCREMENT=122552 DEFAULT CHARSET=latin1;

CREATE TABLE `hhistory` (
  `historyId` int(12) NOT NULL AUTO_INCREMENT,
  `epoch` int(10) DEFAULT NULL,
  `dataType` varchar(10) DEFAULT NULL,
  `poolId` int(18) DEFAULT NULL,
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
  PRIMARY KEY (`historyId`),
  KEY `hh_epoch_dt_pool` (`epoch`,`poolId`,`dataType`),
  KEY `hh_address` (`address`,`dataType`)
) ENGINE=InnoDB AUTO_INCREMENT=642390 DEFAULT CHARSET=latin1;


CREATE TABLE `hpool` (
  `hPoolId` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `identity` varchar(65) DEFAULT NULL,
  `securitycontact` varchar(65) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `address` varchar(128) NOT NULL,
  `details` varchar(500) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `blsKeyCount` int(10) DEFAULT NULL,
  `minSelfDelegation` float(14,2) DEFAULT NULL,
  `maxTotalDelegation` float(18,2) DEFAULT NULL,
  `totalRewards` float(14,2) DEFAULT NULL,
  `createdDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `lastUpdated` timestamp NOT NULL,
  `website` varchar(128) DEFAULT NULL,
  `lifetimeToSign` int(12) DEFAULT NULL,
  `lifetimeApr` float(12,2) DEFAULT NULL,
  `currentEpochSigned` int(12) DEFAULT NULL,
  `currentEpochToSign` int(12) DEFAULT NULL,
  `currentEpochSignPer` float(6,2) DEFAULT NULL,
  `uniqueDelegates` int(10) DEFAULT NULL,
  `fee` float(8,4) DEFAULT NULL,
  `maxFee` float(8,4) DEFAULT NULL,
  `feeChangeRate` float(8,4) DEFAULT NULL,
  `creationBlock` int(10) DEFAULT NULL,
  `lastUpdateBlock` int(10) DEFAULT NULL,
  `totalStaked` float(14,2) DEFAULT NULL,
  `elected` varchar(20) DEFAULT NULL,
  `booted` varchar(20) DEFAULT NULL,
  `optimalBlsKeyCount` int(10) DEFAULT NULL,
  `selfStake` float(14,2) DEFAULT NULL,
  `status` varchar(45) DEFAULT NULL,
  `syncEpochTime` int(12) DEFAULT NULL,
  `bidPerSeat` float(18,0) DEFAULT NULL,
  `lifetimeSigned` int(12) DEFAULT NULL,
  `currentEpochRewards` float(14,2) DEFAULT NULL,
  `prevEpochApr` float(6,2) DEFAULT NULL,
  `prevEpochNetApr` float(6,2) DEFAULT NULL,
  `avgEri` float(6,2) DEFAULT NULL,
  `prevEpochEri` float(6,2) DEFAULT NULL,
  `currentEri` float(6,2) DEFAULT NULL,
  `avgApr` float(6,2) DEFAULT NULL,
  `avgNetApr` float(6,2) DEFAULT NULL,
  `currentApr` float(6,2) DEFAULT NULL,
  `currentNetApr` float(6,2) DEFAULT NULL,
  `activeStatus` varchar(10) DEFAULT NULL,
  `feeChangedEpoch` int(6) DEFAULT NULL,
  `feeChangedDesc` varchar(45) DEFAULT NULL,
  `keepName` varchar(5) DEFAULT 'False',
  PRIMARY KEY (`hPoolId`)
) ENGINE=InnoDB AUTO_INCREMENT=292 DEFAULT CHARSET=latin1;

CREATE TABLE `hpooldel` (
  `poolDelId` int(12) NOT NULL AUTO_INCREMENT,
  `hPoolId` int(5) NOT NULL,
  `address` varchar(128) DEFAULT NULL,
  `stake` float(14,4) DEFAULT NULL,
  `reward` float(12,4) DEFAULT NULL,
  `lastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `createdOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`poolDelId`),
  KEY `pooldel_pool_add_index` (`hPoolId`,`address`)
) ENGINE=InnoDB AUTO_INCREMENT=284128 DEFAULT CHARSET=latin1;

CREATE TABLE `hpooldelhistory` (
  `poolDelId` int(12) NOT NULL AUTO_INCREMENT,
  `hPoolId` int(5) NOT NULL,
  `address` varchar(128) DEFAULT NULL,
  `stake` float(14,4) DEFAULT NULL,
  `reward` float(12,4) DEFAULT NULL,
  `lastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `createdOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `syncTime` timestamp NULL DEFAULT NULL,
  `epochNumber` int(6) DEFAULT NULL,
  PRIMARY KEY (`poolDelId`),
  KEY `hpdh_pool_add_time_index` (`hPoolId`,`address`,`syncTime`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `hpoolperf` (
  `hPoolPerfId` int(11) NOT NULL AUTO_INCREMENT,
  `hPoolId` int(11) NOT NULL,
  `epochNumber` int(10) DEFAULT NULL,
  `mode` varchar(10) DEFAULT NULL,
  `blsKeyCount` int(10) DEFAULT NULL,
  `syncTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `syncEpochTime` int(12) DEFAULT NULL,
  `createdDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `signed` int(12) DEFAULT NULL,
  `askedToSign` int(12) DEFAULT NULL,
  `signPer` float(6,2) DEFAULT NULL,
  `uniqueDelegates` int(10) DEFAULT NULL,
  `totalStaked` float(14,2) DEFAULT NULL,
  `elected` varchar(20) DEFAULT NULL,
  `booted` varchar(20) DEFAULT NULL,
  `selfStake` float(14,2) DEFAULT NULL,
  `status` varchar(45) DEFAULT NULL,
  `bidPerSeat` float(18,0) DEFAULT NULL,
  `fee` float(6,4) DEFAULT NULL,
  `lifetimeSigned` int(12) DEFAULT NULL,
  `lifetimeToSign` int(12) DEFAULT NULL,
  `lifetimeRewards` float(14,2) DEFAULT NULL,
  `rewards` float(14,2) DEFAULT NULL,
  `apr` float(6,2) DEFAULT NULL,
  `netApr` float(6,2) DEFAULT NULL,
  `eri` float(8,2) DEFAULT NULL,
  PRIMARY KEY (`hPoolPerfId`),
  KEY `in_hpp_mode_epoch_elected` (`epochNumber`,`mode`,`elected`),
  KEY `in_hpp_mode_pool` (`hPoolId`,`mode`)
) ENGINE=InnoDB AUTO_INCREMENT=590353 DEFAULT CHARSET=latin1;


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


INSERT INTO `coinstat` (`totalStake`,`stakingPools`,`currentRewardRate`,`ssStake`,`totalSupply`,`circulatingSupply`,`symbol`,`lastUpdated`,`btcPrice`,`usdPrice`,`ssBlocks`,`ssRewards`,`recentBlock`,`blocks_8hrs`,`blocks_24hrs`,`blocks_7days`,`blocks_1hr`,`withdrawSyncTillBlock`,`uniqueDelegates`,`coinId`,`totalRewardWithdrawals`,`activeAccounts`,`totalPoolStake`,`totalSoloStake`,`percentStaked`,`usdStaked`,`usdMcap`,`priceChangeUsd`,`rewardsBalance`,`blocks_21days`,`actualRewardRate`,`blockRate`,`medianRawStake`,`isSynced`,`stakeSupply`,`electedPools`,`totalWeightedStake`,`otherArr`,`epochLastBlock`,`nextEpochTime`,`currentEpoch`) VALUES (3856964608.00,292,11.43,NULL,12600000512,6963899392,'HARMONY','2020-08-29 02:18:22',0.00000094,0.01075,NULL,NULL,4601624,NULL,NULL,NULL,NULL,NULL,1820,'4',NULL,NULL,NULL,NULL,55.4,41471132,66758296,-2.16,NULL,NULL,NULL,NULL,5827559,NULL,NULL,NULL,NULL,NULL,4603902,1598678879,260);
INSERT INTO `syncstatus` (`app`,`syncType`,`syncedTillEpochTime`,`syncedTillBlock`,`lastUpdated`,`syncCategory`,`syncedTillEpoch`) VALUES ('HARMONY','AddressHistory',NULL,NULL,'2020-08-28 06:51:23','History',260);
INSERT INTO `eventlog` (`eventName`,`description`,`eventTime`,`app`) VALUES ('harmonyLastSyncedEventBlockHeight','3341867',1493122425,'HARMONY');
