package contrib

import (
	autocliv1 "cosmossdk.io/api/cosmos/autocli/v1"

	"contribledger/x/contrib/types"
)

// AutoCLIOptions implements the autocli.HasAutoCLIConfig interface.
func (am AppModule) AutoCLIOptions() *autocliv1.ModuleOptions {
	return &autocliv1.ModuleOptions{
		Query: &autocliv1.ServiceCommandDescriptor{
			Service: types.Query_serviceDesc.ServiceName,
			RpcCommandOptions: []*autocliv1.RpcCommandOptions{
				{
					RpcMethod: "Params",
					Use:       "params",
					Short:     "Shows the parameters of the module",
				},
				{
					RpcMethod: "ListContribution",
					Use:       "list-contribution",
					Short:     "List all contribution",
				},
				{
					RpcMethod:      "GetContribution",
					Use:            "get-contribution [id]",
					Short:          "Gets a contribution",
					Alias:          []string{"show-contribution"},
					PositionalArgs: []*autocliv1.PositionalArgDescriptor{{ProtoField: "index"}},
				},
				// this line is used by ignite scaffolding # autocli/query
			},
		},
		Tx: &autocliv1.ServiceCommandDescriptor{
			Service:              types.Msg_serviceDesc.ServiceName,
			EnhanceCustomCommand: true, // only required if you want to use the custom command
			RpcCommandOptions: []*autocliv1.RpcCommandOptions{
				{
					RpcMethod: "UpdateParams",
					Skip:      true, // skipped because authority gated
				},
				{
					RpcMethod:      "SubmitContribution",
					Use:            "submit-contribution [user-id] [weight-update] [convergence-speed] [accuracy-improvement] [contribution-score]",
					Short:          "Send a submitContribution tx",
					PositionalArgs: []*autocliv1.PositionalArgDescriptor{{ProtoField: "user_id"}, {ProtoField: "weight_update"}, {ProtoField: "convergence_speed"}, {ProtoField: "accuracy_improvement"}, {ProtoField: "contribution_score"}},
				},
				{
					RpcMethod:      "CreateContribution",
					Use:            "create-contribution [index] [user-id] [weight-update] [convergence-speed] [accuracy-improvement] [contribution-score] [timestamp]",
					Short:          "Create a new contribution",
					PositionalArgs: []*autocliv1.PositionalArgDescriptor{{ProtoField: "index"}, {ProtoField: "user_id"}, {ProtoField: "weight_update"}, {ProtoField: "convergence_speed"}, {ProtoField: "accuracy_improvement"}, {ProtoField: "contribution_score"}, {ProtoField: "timestamp"}},
				},
				{
					RpcMethod:      "UpdateContribution",
					Use:            "update-contribution [index] [user-id] [weight-update] [convergence-speed] [accuracy-improvement] [contribution-score] [timestamp]",
					Short:          "Update contribution",
					PositionalArgs: []*autocliv1.PositionalArgDescriptor{{ProtoField: "index"}, {ProtoField: "user_id"}, {ProtoField: "weight_update"}, {ProtoField: "convergence_speed"}, {ProtoField: "accuracy_improvement"}, {ProtoField: "contribution_score"}, {ProtoField: "timestamp"}},
				},
				{
					RpcMethod:      "DeleteContribution",
					Use:            "delete-contribution [index]",
					Short:          "Delete contribution",
					PositionalArgs: []*autocliv1.PositionalArgDescriptor{{ProtoField: "index"}},
				},
				// this line is used by ignite scaffolding # autocli/tx
			},
		},
	}
}
