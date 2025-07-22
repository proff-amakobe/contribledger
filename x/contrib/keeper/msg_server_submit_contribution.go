package keeper

import (
	"context"
	"strconv"

	"contribledger/x/contrib/types"

	sdk "github.com/cosmos/cosmos-sdk/types"
)

func (k msgServer) SubmitContribution(goCtx context.Context, msg *types.MsgSubmitContribution) (*types.MsgSubmitContributionResponse, error) {
	ctx := sdk.UnwrapSDKContext(goCtx)

	// Calculate contribution score using the formula
	calculatedScore := uint64(0.35*float64(msg.WeightUpdate) + 0.30*float64(msg.ConvergenceSpeed) + 0.35*float64(msg.AccuracyImprovement))

	// Create a unique index for this contribution
	contributionIndex := strconv.FormatInt(ctx.BlockHeight(), 10) + "-" + msg.UserId

	// Use the generated CreateContribution message instead of direct storage
	createMsg := &types.MsgCreateContribution{
		Creator:             msg.Creator,
		Index:               contributionIndex,
		UserId:              msg.UserId,
		WeightUpdate:        msg.WeightUpdate,
		ConvergenceSpeed:    msg.ConvergenceSpeed,
		AccuracyImprovement: msg.AccuracyImprovement,
		ContributionScore:   calculatedScore,
		Timestamp:           ctx.BlockTime().Unix(),
	}

	// Call the generated CreateContribution method
	_, err := k.CreateContribution(ctx, createMsg)
	if err != nil {
		return nil, err
	}

	// Emit event
	ctx.EventManager().EmitEvent(
		sdk.NewEvent(
			types.EventTypeContributionSubmitted,
			sdk.NewAttribute(types.AttributeKeyUserID, msg.UserId),
			sdk.NewAttribute(types.AttributeKeyScore, strconv.FormatUint(calculatedScore, 10)),
		),
	)

	return &types.MsgSubmitContributionResponse{}, nil
}
