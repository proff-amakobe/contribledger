package types

import "fmt"

// DefaultGenesis returns the default genesis state
func DefaultGenesis() *GenesisState {
	return &GenesisState{
		Params:          DefaultParams(),
		ContributionMap: []Contribution{}}
}

// Validate performs basic genesis state validation returning an error upon any
// failure.
func (gs GenesisState) Validate() error {
	contributionIndexMap := make(map[string]struct{})

	for _, elem := range gs.ContributionMap {
		index := fmt.Sprint(elem.Index)
		if _, ok := contributionIndexMap[index]; ok {
			return fmt.Errorf("duplicated index for contribution")
		}
		contributionIndexMap[index] = struct{}{}
	}

	return gs.Params.Validate()
}
