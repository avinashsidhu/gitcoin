cap prog drop center
prog center, rclass
    syntax varlist(min=1) [if]
    
    foreach var of varlist `varlist' {
        local lab: variable label `var'
        su `var' `if'
        gen `var'_cen = `var' - r(mean)
        label var `var'_cen "`lab'"

        return local `var' `var'_cen
    }

end