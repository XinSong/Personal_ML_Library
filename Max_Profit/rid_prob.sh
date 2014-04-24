#!/bin/bash
awk 'BEGIN{OFS="\t";
		rank = 1
		while(getline<"score_probability")
		{
			floor[rank] = $1
			ceiling[rank] =$2
			prob[rank] = $3
			unpaid_frac[rank] = $5
			rank++
		}
	}
	{
		rid = $1
		i = 1
		last_prob = 0
		last_ratio = 0
		while(i<rank)
		{
			if( $2 >= floor[i] )
			{
				last_prob = prob[i]
				last_ratio = unpaid_frac[i]
				if( $2 <= ceiling[i]){
					score[rid] = prob[i]
					ratio[rid] = unpaid_frac[i]
					break
				}
			}
			else if($2 < floor[i])
			{
				score[rid] = (last_prob + prob[i])/2
				ratio[rid] = (last_ratio + ratio[i])/2
				break
			}
			i++
		}
		print rid,score[rid],ratio[rid]
	}' credit_loan/score_test.txt
