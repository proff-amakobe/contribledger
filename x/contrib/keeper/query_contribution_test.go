package keeper_test

import (
	"context"
	"strconv"
	"testing"

	"github.com/cosmos/cosmos-sdk/types/query"
	"github.com/stretchr/testify/require"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"contribledger/x/contrib/keeper"
	"contribledger/x/contrib/types"
)

func createNContribution(keeper keeper.Keeper, ctx context.Context, n int) []types.Contribution {
	items := make([]types.Contribution, n)
	for i := range items {
		items[i].Index = strconv.Itoa(i)
		items[i].UserId = strconv.Itoa(i)
		items[i].WeightUpdate = uint64(i)
		items[i].ConvergenceSpeed = uint64(i)
		items[i].AccuracyImprovement = uint64(i)
		items[i].ContributionScore = uint64(i)
		items[i].Timestamp = int64(i)
		_ = keeper.Contribution.Set(ctx, items[i].Index, items[i])
	}
	return items
}

func TestContributionQuerySingle(t *testing.T) {
	f := initFixture(t)
	qs := keeper.NewQueryServerImpl(f.keeper)
	msgs := createNContribution(f.keeper, f.ctx, 2)
	tests := []struct {
		desc     string
		request  *types.QueryGetContributionRequest
		response *types.QueryGetContributionResponse
		err      error
	}{
		{
			desc: "First",
			request: &types.QueryGetContributionRequest{
				Index: msgs[0].Index,
			},
			response: &types.QueryGetContributionResponse{Contribution: msgs[0]},
		},
		{
			desc: "Second",
			request: &types.QueryGetContributionRequest{
				Index: msgs[1].Index,
			},
			response: &types.QueryGetContributionResponse{Contribution: msgs[1]},
		},
		{
			desc: "KeyNotFound",
			request: &types.QueryGetContributionRequest{
				Index: strconv.Itoa(100000),
			},
			err: status.Error(codes.NotFound, "not found"),
		},
		{
			desc: "InvalidRequest",
			err:  status.Error(codes.InvalidArgument, "invalid request"),
		},
	}
	for _, tc := range tests {
		t.Run(tc.desc, func(t *testing.T) {
			response, err := qs.GetContribution(f.ctx, tc.request)
			if tc.err != nil {
				require.ErrorIs(t, err, tc.err)
			} else {
				require.NoError(t, err)
				require.EqualExportedValues(t, tc.response, response)
			}
		})
	}
}

func TestContributionQueryPaginated(t *testing.T) {
	f := initFixture(t)
	qs := keeper.NewQueryServerImpl(f.keeper)
	msgs := createNContribution(f.keeper, f.ctx, 5)

	request := func(next []byte, offset, limit uint64, total bool) *types.QueryAllContributionRequest {
		return &types.QueryAllContributionRequest{
			Pagination: &query.PageRequest{
				Key:        next,
				Offset:     offset,
				Limit:      limit,
				CountTotal: total,
			},
		}
	}
	t.Run("ByOffset", func(t *testing.T) {
		step := 2
		for i := 0; i < len(msgs); i += step {
			resp, err := qs.ListContribution(f.ctx, request(nil, uint64(i), uint64(step), false))
			require.NoError(t, err)
			require.LessOrEqual(t, len(resp.Contribution), step)
			require.Subset(t, msgs, resp.Contribution)
		}
	})
	t.Run("ByKey", func(t *testing.T) {
		step := 2
		var next []byte
		for i := 0; i < len(msgs); i += step {
			resp, err := qs.ListContribution(f.ctx, request(next, 0, uint64(step), false))
			require.NoError(t, err)
			require.LessOrEqual(t, len(resp.Contribution), step)
			require.Subset(t, msgs, resp.Contribution)
			next = resp.Pagination.NextKey
		}
	})
	t.Run("Total", func(t *testing.T) {
		resp, err := qs.ListContribution(f.ctx, request(nil, 0, 0, true))
		require.NoError(t, err)
		require.Equal(t, len(msgs), int(resp.Pagination.Total))
		require.EqualExportedValues(t, msgs, resp.Contribution)
	})
	t.Run("InvalidRequest", func(t *testing.T) {
		_, err := qs.ListContribution(f.ctx, nil)
		require.ErrorIs(t, err, status.Error(codes.InvalidArgument, "invalid request"))
	})
}
