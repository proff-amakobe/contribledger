package types

import (
	errorsmod "cosmossdk.io/errors"
	sdk "github.com/cosmos/cosmos-sdk/types"
	sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"
)

func (msg *MsgSubmitContribution) ValidateBasic() error {
	_, err := sdk.AccAddressFromBech32(msg.Creator)
	if err != nil {
		return errorsmod.Wrapf(sdkerrors.ErrInvalidAddress, "invalid creator address (%s)", err)
	}

	// Validate contribution metrics are within 0-100 range
	if msg.WeightUpdate > 100 || msg.ConvergenceSpeed > 100 || msg.AccuracyImprovement > 100 {
		return errorsmod.Wrap(sdkerrors.ErrInvalidRequest, "metrics must be normalized to 0-100 range")
	}

	return nil
}
