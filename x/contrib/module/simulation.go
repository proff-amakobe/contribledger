package contrib

import (
	"math/rand"

	"github.com/cosmos/cosmos-sdk/types/module"
	simtypes "github.com/cosmos/cosmos-sdk/types/simulation"
	"github.com/cosmos/cosmos-sdk/x/simulation"

	"contribledger/testutil/sample"
	contribsimulation "contribledger/x/contrib/simulation"
	"contribledger/x/contrib/types"
)

// GenerateGenesisState creates a randomized GenState of the module.
func (AppModule) GenerateGenesisState(simState *module.SimulationState) {
	accs := make([]string, len(simState.Accounts))
	for i, acc := range simState.Accounts {
		accs[i] = acc.Address.String()
	}
	contribGenesis := types.GenesisState{
		Params: types.DefaultParams(),
		ContributionMap: []types.Contribution{{Creator: sample.AccAddress(),
			Index: "0",
		}, {Creator: sample.AccAddress(),
			Index: "1",
		}}}
	simState.GenState[types.ModuleName] = simState.Cdc.MustMarshalJSON(&contribGenesis)
}

// RegisterStoreDecoder registers a decoder.
func (am AppModule) RegisterStoreDecoder(_ simtypes.StoreDecoderRegistry) {}

// WeightedOperations returns the all the gov module operations with their respective weights.
func (am AppModule) WeightedOperations(simState module.SimulationState) []simtypes.WeightedOperation {
	operations := make([]simtypes.WeightedOperation, 0)
	const (
		opWeightMsgSubmitContribution          = "op_weight_msg_contrib"
		defaultWeightMsgSubmitContribution int = 100
	)

	var weightMsgSubmitContribution int
	simState.AppParams.GetOrGenerate(opWeightMsgSubmitContribution, &weightMsgSubmitContribution, nil,
		func(_ *rand.Rand) {
			weightMsgSubmitContribution = defaultWeightMsgSubmitContribution
		},
	)
	operations = append(operations, simulation.NewWeightedOperation(
		weightMsgSubmitContribution,
		contribsimulation.SimulateMsgSubmitContribution(am.authKeeper, am.bankKeeper, am.keeper, simState.TxConfig),
	))
	const (
		opWeightMsgCreateContribution          = "op_weight_msg_contrib"
		defaultWeightMsgCreateContribution int = 100
	)

	var weightMsgCreateContribution int
	simState.AppParams.GetOrGenerate(opWeightMsgCreateContribution, &weightMsgCreateContribution, nil,
		func(_ *rand.Rand) {
			weightMsgCreateContribution = defaultWeightMsgCreateContribution
		},
	)
	operations = append(operations, simulation.NewWeightedOperation(
		weightMsgCreateContribution,
		contribsimulation.SimulateMsgCreateContribution(am.authKeeper, am.bankKeeper, am.keeper, simState.TxConfig),
	))
	const (
		opWeightMsgUpdateContribution          = "op_weight_msg_contrib"
		defaultWeightMsgUpdateContribution int = 100
	)

	var weightMsgUpdateContribution int
	simState.AppParams.GetOrGenerate(opWeightMsgUpdateContribution, &weightMsgUpdateContribution, nil,
		func(_ *rand.Rand) {
			weightMsgUpdateContribution = defaultWeightMsgUpdateContribution
		},
	)
	operations = append(operations, simulation.NewWeightedOperation(
		weightMsgUpdateContribution,
		contribsimulation.SimulateMsgUpdateContribution(am.authKeeper, am.bankKeeper, am.keeper, simState.TxConfig),
	))
	const (
		opWeightMsgDeleteContribution          = "op_weight_msg_contrib"
		defaultWeightMsgDeleteContribution int = 100
	)

	var weightMsgDeleteContribution int
	simState.AppParams.GetOrGenerate(opWeightMsgDeleteContribution, &weightMsgDeleteContribution, nil,
		func(_ *rand.Rand) {
			weightMsgDeleteContribution = defaultWeightMsgDeleteContribution
		},
	)
	operations = append(operations, simulation.NewWeightedOperation(
		weightMsgDeleteContribution,
		contribsimulation.SimulateMsgDeleteContribution(am.authKeeper, am.bankKeeper, am.keeper, simState.TxConfig),
	))

	return operations
}

// ProposalMsgs returns msgs used for governance proposals for simulations.
func (am AppModule) ProposalMsgs(simState module.SimulationState) []simtypes.WeightedProposalMsg {
	return []simtypes.WeightedProposalMsg{}
}
