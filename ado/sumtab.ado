cap prog drop sumtab
prog sumtab
	syntax varlist(min=1) [fw aw pw] [if], output(string) title(string)
	
	matrix drop _all

	** Descriptive statistics
	estpost summarize `varlist' `if', listwise
	matrix table = ( e(count) \ e(mean) \ e(sd) )
	matrix rownames table = count mean sd
	matrix list table

	** Correlation matrix
	correlate `varlist' `if'
	matrix C = r(C)
	local corr : rownames C
	matrix table = ( table \ C )
	matrix list table

	estadd matrix table = table
	eststo sumtab

	/* local cells table[count](fmt(0) label(Count)) table[mean](fmt(2) label(Mean)) table[sd](fmt(2) label(SD)) */
	local cells table[mean](fmt(2) label(Mean)) table[sd](fmt(2) label(SD))
	local collab
	local drop
	local i = 0
	foreach row of local corr {
		local drop `drop' `row'
		local cells `cells' table[`row']( fmt(3) drop(`drop') label((`++i')) )
		local lbl: variable label `row'
		local collab `" `collab' `row' "(`i') `lbl'" "'
	}
// 	display "`cells'"
// 	display `"`collab'"'

	esttab sumtab using `output', ///
        replace ///
		nolz ///
        nonumbers ///
        compress ///
        cells("`cells'") ///
        coeflabels(`collab') ///
		title({\f1\b `title'}) ///
		fonttbl(\f0\fnil Arial;\f1\fnil Times New Roman;)

end
