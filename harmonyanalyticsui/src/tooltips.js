import UIUtils from "./util/UIUtils";
import text from "./text";

export default {
  networkCharts: {
    stakeHistory: UIUtils.getTip("Chart reflecting Total Staked amount in $ONE with every passing epoch"),
    activeAddress: UIUtils.getTip("Chart showing growth of active harmony addresses with every passing epoch"),
    uniqueDelegates: UIUtils.getTip("Chart showing total number of unique delegates in the network with every passing epoch"),
    circulatingSupply: UIUtils.getTip("Chart reflecting how circulating supply of $ONE is growing over time"),
    medianRawStake: UIUtils.getTip("Chart showing median raw stake for bidding auctions per epoch"),
    validatorCount: UIUtils.getTip("Chart showing total number of validators in the network with every passing epoch"),
    signPercentage: UIUtils.getTip("Chart showing overall sign percentage of all elected validators per epoch"),
    expectedReturns: UIUtils.getTip("Chart showing how expected returns from staking are changing with every passing epoch"),
    transactionGrowth: UIUtils.getTip("Chart showing total network transaction over time"),
    txComparison: UIUtils.getTip("Chart showing comparison of daily transactions related to staking (Delegations, Undelegations, Validator changes etc) and rest of the transactions"),
    dailyTransactions: UIUtils.getTip("Chart showing network transactions executed on a daily basis"),
    shardDistribution: UIUtils.getTip("Chart showing distribution of transactions over all harmony shards. Shard 0 is the beacon shard and has extra responsibilities as compared to the rest of the shards"),
    blockRate: UIUtils.getTip("Chart showing block production rate of all shards by epoch"),
    nodeVersionSummary: UIUtils.getTip("Chart showing distribution of software version by BLS Keys"),
  },
  address: {
    rewardRatio: UIUtils.getTip("Chart showing reward ratio for all delegations of an address. Reward Ratio - Indicates the relative performance of a delegation as compared to rest of the delegations for the address. A ratio of 1 means that performance is average. A ratio >1 means that a delegation performed better than average and a ratio <1 means that a delegation performed worse than average."),
    stakeHistory: UIUtils.getTip("Chart showing stake history for an address"),
    rewardsSummary: UIUtils.getTip("Chart showing unclaimed rewards balance for the addressat the end of every epoch."),
  },
  valDetailsCharts: {
    hourlySignPer: UIUtils.getTip("Chart showing hourly sign percentages for the validator. Click more/less to change the timeframe for chart."),
    hourlySigns: UIUtils.getTip("Chart showing hourly signatures for the validator. Click more/less to change the timeframe for chart."),
    epochSignPer: UIUtils.getTip("Chart showing epoch sign percentages for the validator. Click more/less to change the timeframe for chart."),
    epochSigns: UIUtils.getTip("Chart showing epoch signatures for the validator. Click more/less to change the timeframe for chart."),
  },
  valStats: {
    eriHistory: UIUtils.getTip("Chart showing Expected Returns Index (ERI) history of validator. " + text.eri),
    erHistory: UIUtils.getTip("Chart showing Expected Returns (ER) history of validator. "),
    stakeHistory: UIUtils.getTip("Chart showing stake history of validator. "),
    delegateHistory: UIUtils.getTip("Chart showing unique delegate count history of validator. "),
  },
};
