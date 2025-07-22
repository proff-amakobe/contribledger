package keeper

import (
	"context"
	"errors"
	"fmt"

	"contribledger/x/contrib/types"

	"cosmossdk.io/collections"
	errorsmod "cosmossdk.io/errors"
	sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"
)

func (k msgServer) CreateContribution(ctx context.Context, msg *types.MsgCreateContribution) (*types.MsgCreateContributionResponse, error) {
	if _, err := k.addressCodec.StringToBytes(msg.Creator); err != nil {
		return nil, errorsmod.Wrap(sdkerrors.ErrInvalidAddress, fmt.Sprintf("invalid address: %s", err))
	}

	// Check if the value already exists
	ok, err := k.Contribution.Has(ctx, msg.Index)
	if err != nil {
		return nil, errorsmod.Wrap(sdkerrors.ErrLogic, err.Error())
	} else if ok {
		return nil, errorsmod.Wrap(sdkerrors.ErrInvalidRequest, "index already set")
	}

	var contribution = types.Contribution{
		Creator:             msg.Creator,
		Index:               msg.Index,
		UserId:              msg.UserId,
		WeightUpdate:        msg.WeightUpdate,
		ConvergenceSpeed:    msg.ConvergenceSpeed,
		AccuracyImprovement: msg.AccuracyImprovement,
		ContributionScore:   msg.ContributionScore,
		Timestamp:           msg.Timestamp,
	}

	if err := k.Contribution.Set(ctx, contribution.Index, contribution); err != nil {
		return nil, errorsmod.Wrap(sdkerrors.ErrLogic, err.Error())
	}

	return &types.MsgCreateContributionResponse{}, nil
}

func (k msgServer) UpdateContribution(ctx context.Context, msg *types.MsgUpdateContribution) (*types.MsgUpdateContributionResponse, error) {
	if _, err := k.addressCodec.StringToBytes(msg.Creator); err != nil {
		return nil, errorsmod.Wrap(sdkerrors.ErrInvalidAddress, fmt.Sprintf("invalid signer address: %s", err))
	}

	// Check if the value exists
	val, err := k.Contribution.Get(ctx, msg.Index)
	if err != nil {
		if errors.Is(err, collections.ErrNotFound) {
			return nil, errorsmod.Wrap(sdkerrors.ErrKeyNotFound, "index not set")
		}

		return nil, errorsmod.Wrap(sdkerrors.ErrLogic, err.Error())
	}

	// Checks if the msg creator is the same as the current owner
	if msg.Creator != val.Creator {
		return nil, errorsmod.Wrap(sdkerrors.ErrUnauthorized, "incorrect owner")
	}

	var contribution = types.Contribution{
		Creator:             msg.Creator,
		Index:               msg.Index,
		UserId:              msg.UserId,
		WeightUpdate:        msg.WeightUpdate,
		ConvergenceSpeed:    msg.ConvergenceSpeed,
		AccuracyImprovement: msg.AccuracyImprovement,
		ContributionScore:   msg.ContributionScore,
		Timestamp:           msg.Timestamp,
	}

	if err := k.Contribution.Set(ctx, contribution.Index, contribution); err != nil {
		return nil, errorsmod.Wrap(sdkerrors.ErrLogic, "failed to update contribution")
	}

	return &types.MsgUpdateContributionResponse{}, nil
}

func (k msgServer) DeleteContribution(ctx context.Context, msg *types.MsgDeleteContribution) (*types.MsgDeleteContributionResponse, error) {
	if _, err := k.addressCodec.StringToBytes(msg.Creator); err != nil {
		return nil, errorsmod.Wrap(sdkerrors.ErrInvalidAddress, fmt.Sprintf("invalid signer address: %s", err))
	}

	// Check if the value exists
	val, err := k.Contribution.Get(ctx, msg.Index)
	if err != nil {
		if errors.Is(err, collections.ErrNotFound) {
			return nil, errorsmod.Wrap(sdkerrors.ErrKeyNotFound, "index not set")
		}

		return nil, errorsmod.Wrap(sdkerrors.ErrLogic, err.Error())
	}

	// Checks if the msg creator is the same as the current owner
	if msg.Creator != val.Creator {
		return nil, errorsmod.Wrap(sdkerrors.ErrUnauthorized, "incorrect owner")
	}

	if err := k.Contribution.Remove(ctx, msg.Index); err != nil {
		return nil, errorsmod.Wrap(sdkerrors.ErrLogic, "failed to remove contribution")
	}

	return &types.MsgDeleteContributionResponse{}, nil
}
