* regionpair2 has errors. Fix later.
cap prog drop groupcf
prog groupcf, rclass
    syntax varlist(min=1), m1(string) m2(string) se(string)

	eststo m1: reg `m1'
	eststo m2: reg `m2'
	suest m1 m2, `se'

	foreach var in `varlist' {
		test [m1_mean]`var'=[m2_mean]`var'
		return local `var'=r(p)
	}
	eststo drop m1 m2
end