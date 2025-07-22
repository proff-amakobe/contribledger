package keeper

import (
	"context"
	"errors"

	"contribledger/x/contrib/types"

	"cosmossdk.io/collections"
	"github.com/cosmos/cosmos-sdk/types/query"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func (q queryServer) ListContribution(ctx context.Context, req *types.QueryAllContributionRequest) (*types.QueryAllContributionResponse, error) {
	if req == nil {
		return nil, status.Error(codes.InvalidArgument, "invalid request")
	}

	contributions, pageRes, err := query.CollectionPaginate(
		ctx,
		q.k.Contribution,
		req.Pagination,
		func(_ string, value types.Contribution) (types.Contribution, error) {
			return value, nil
		},
	)
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	return &types.QueryAllContributionResponse{Contribution: contributions, Pagination: pageRes}, nil
}

func (q queryServer) GetContribution(ctx context.Context, req *types.QueryGetContributionRequest) (*types.QueryGetContributionResponse, error) {
	if req == nil {
		return nil, status.Error(codes.InvalidArgument, "invalid request")
	}

	val, err := q.k.Contribution.Get(ctx, req.Index)
	if err != nil {
		if errors.Is(err, collections.ErrNotFound) {
			return nil, status.Error(codes.NotFound, "not found")
		}

		return nil, status.Error(codes.Internal, "internal error")
	}

	return &types.QueryGetContributionResponse{Contribution: val}, nil
}
