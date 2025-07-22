package types

import (
	errorsmod "cosmossdk.io/errors"
)

var (
	ErrInvalidContributionScore = errorsmod.Register(ModuleName, 1, "invalid contribution score")
	ErrContributionNotFound     = errorsmod.Register(ModuleName, 2, "contribution not found")
	ErrInvalidSigner            = errorsmod.Register(ModuleName, 3, "invalid signer")
	ErrSample                   = errorsmod.Register(ModuleName, 1100, "sample error")
	ErrInvalidRequest           = errorsmod.Register(ModuleName, 4, "invalid request")
	ErrUnauthorized             = errorsmod.Register(ModuleName, 5, "unauthorized")
)
