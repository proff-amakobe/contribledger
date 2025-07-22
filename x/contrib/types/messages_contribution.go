package types

func NewMsgCreateContribution(
	creator string,
	index string,
	userId string,
	weightUpdate uint64,
	convergenceSpeed uint64,
	accuracyImprovement uint64,
	contributionScore uint64,
	timestamp int64,

) *MsgCreateContribution {
	return &MsgCreateContribution{
		Creator:             creator,
		Index:               index,
		UserId:              userId,
		WeightUpdate:        weightUpdate,
		ConvergenceSpeed:    convergenceSpeed,
		AccuracyImprovement: accuracyImprovement,
		ContributionScore:   contributionScore,
		Timestamp:           timestamp,
	}
}

func NewMsgUpdateContribution(
	creator string,
	index string,
	userId string,
	weightUpdate uint64,
	convergenceSpeed uint64,
	accuracyImprovement uint64,
	contributionScore uint64,
	timestamp int64,

) *MsgUpdateContribution {
	return &MsgUpdateContribution{
		Creator:             creator,
		Index:               index,
		UserId:              userId,
		WeightUpdate:        weightUpdate,
		ConvergenceSpeed:    convergenceSpeed,
		AccuracyImprovement: accuracyImprovement,
		ContributionScore:   contributionScore,
		Timestamp:           timestamp,
	}
}

func NewMsgDeleteContribution(
	creator string,
	index string,

) *MsgDeleteContribution {
	return &MsgDeleteContribution{
		Creator: creator,
		Index:   index,
	}
}
