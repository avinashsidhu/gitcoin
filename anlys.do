*------------------------------------------------------
* Gitcoin analysis
* ICIS
* Created: 4/21/2022
* Updated: 4/21/2022
*------------------------------------------------------

use "var/cache/bounty2.dta", clear

destring github_comments value_in_usdt delayed_days elapased_days_from_created elapased_days_from_start num_fulfillments num_interests ///
    token_ratio totalearned totalfulfillments totalhours totalownedbounties totalsubs ///
    github_stats_org_followers github_stats_org_following github_stats_org_public_repos ///
    github_stats_repo_forks_count github_stats_repo_stars_count github_stats_issue_comments_coun ///
    github_stats_user_followers github_stats_user_following github_stats_user_public_repos ///
    coin_stats_volume coin_stats_prob_not_zero coin_stats_price coin_stats_avg_price coin_stats_avg_return coin_stats_std_return coin_stats_kurt_return coin_stats_skew_return coin_stats_momentum coin_stats_roc ///
    github_owner_tenure github_user_tenure ///
    , replace force

rename github_stats_* *

foreach var in submitted cancelled accepted {
    rename `var' `var'2
    encode `var'2, gen(`var')
    replace `var' = `var'-1
    label value `var'
    drop `var'2
}

replace bounty_type = "Documentation" if bounty_type=="belgeler"
replace bounty_type = "Feature" if bounty_type=="Funkcja"
replace bounty_type = "Other" if bounty_type=="Andere"
replace bounty_type = "Design" if bounty_type=="设计"
replace bounty_type = "" if inlist(bounty_type, "æ¹å", "0")

replace project_length = "Months" if inlist(project_length, "Miesięcy", "ay")
replace project_length = "Days" if inlist(project_length, "Tage")
replace project_length = "Weeks" if inlist(project_length, "周")
replace project_length = "" if inlist(project_length, "0")

replace experience_level = "Beginner" if inlist(experience_level, "beginner")
replace experience_level = "Intermediate" if inlist(experience_level, "Mittlere", "Pośredni", "中间的")
replace experience_level = "Advanced" if inlist(experience_level, "advanced", "ileri")
replace experience_level = "" if inlist(experience_level, "0", "åå¿è")

gen coin_status = "Not listed" if coin_stats_before_listed==""
replace coin_status = "Before listed" if coin_stats_before_listed=="True"
replace coin_status = "Listed" if coin_stats_before_listed=="False"

foreach var in org_name project_type comp_type permission_type bounty_type project_length experience_level coin_status {
    encode `var', gen(`var'_id)
}

replace github_owner_tenure = 0 if github_owner_tenure<0
replace github_user_tenure = 0 if github_user_tenure<0

replace comp_type_id=0 if comp_type_id==3

gen hourlyrate = totalearned/totalhours
replace hourlyrate = 0 if totalsubs==0

replace elapased_days_from_created = . if !submitted
* github_stats_user_twitter_userna if not None

gen date = date(created,"YMD")
gen year = year(date)

local varlist value_in_usdt num_interests num_fulfillments totalhours totalsubs totalfulfillments totalearned hourlyrate org_public_repos repo_forks_count repo_stars_count issue_comments_coun user_followers user_following user_public_repos coin_stats_volume totalownedbounties github_owner_tenure github_user_tenure coin_stats_std_return
foreach var in `varlist' {
    gen ln`var' = ln(1+`var')
}

gen risk = 1 if comp_type=="fiat"
replace risk = 2 if comp_type=="stable"
replace risk = 3 if comp_type=="coin"
replace risk = 4 if comp_type=="token"

gen project_length_cont = 0 if project_length=="Unknown"
replace project_length_cont = 1 if project_length=="Hours"
replace project_length_cont = 2 if project_length=="Days"
replace project_length_cont = 3 if project_length=="Weeks"
replace project_length_cont = 4 if project_length=="Months"

gen project_difficulty_cont = 0 if experience_level=="Beginner"
replace project_difficulty_cont = 1 if experience_level=="Intermediate"
replace project_difficulty_cont = 2 if experience_level=="Advanced"

* remove outliers (n=4)
drop if coin_stats_avg_return>0.4&!mi(coin_stats_avg_return) // arbitrary cutoff

* github_comments, elapsed_days_without_sub
* token_ratio

xtile value_cat = lnvalue, nq(3)

gen gain_domain = (coin_stats_avg_return>=0)
gen return_domain = 1 if coin_stats_avg_return<0&coin_stats_prob_not_zero<=.10
replace return_domain = 2 if coin_stats_prob_not_zero>.1
replace return_domain = 3 if coin_stats_avg_return>0&coin_stats_prob_not_zero<=.1

gen longer_than_day = (project_length_id!=2)


* Label
lab var num_interests "Number of applicants"
lab var lnnum_interests "Number of applicants"
lab var lntotalhours "Average hours worked"
lab var lntotalsubs "Average submissions"
lab var lntotalfulfillments "Average fulfillments"
lab var lntotalearned "Average total earned"
lab var lnhourlyrate "Average hourly rate"
lab var submitted "Submitted"
lab var accepted "Accepted"

lab var lnvalue_in_usdt "Bounty value"
lab define value 1 "Value low" 2 "Value medium" 3 "Value high"
lab value value_cat value
lab var coin_stats_std_return "Price volatility"

lab var project_difficulty_cont "Recommended experience level"
lab var project_length_cont "Expected project length"
lab var permission_type_id "Permissionless bounty"
lab define permission 1 "Approval" 2 "Permissionless"
lab value permission_type_id permission

lab var lnrepo_stars_count "Owner github repo stars"
lab var lnuser_followers "Owner followers"
lab var lnuser_public_repos "Owner repos"
lab var lnorg_public_repos "Owner organization repos"
lab var lngithub_user_tenure "Owner github tenure"
lab var lngithub_owner_tenure "Owner organization github tenure"
lab var lntotalownedbounties "Owner previous bounties"

*** Run models
* DVs
// local participation lnnum_interests lntotalhours lntotalsubs lntotalearned lnhourlyrate
local participation lnnum_interests lntotalhours lntotalearned
local delays
local performance submitted accepted // cancelled 
local dvs `participation' `performance'

// local ivs risk lnvalue coin_stats_avg_return coin_stats_std_return
local ivs lnvalue ib2.coin_status_id i.comp_type_id
local ivs lnvalue i.comp_type_id lncoin_stats_volume
local ivs lnvalue coin_stats_std_return
local ivs lnvalue i.comp_type_id i.std_cat
local ivs lnvalue comp_type_id##c.coin_stats_std_return
local ivs comp_type_id##c.lnvalue
local ivs lnvalue gain_domain##c.(coin_stats_std_return)

local ivs lnvalue coin_stats_std_return
local ivs2 c.(lnvalue)##c.(coin_stats_std_return)
local ivs3 i.value_cat##c.coin_stats_std_return

* Controls
local bounty_ctr project_difficulty_cont project_length_cont i.permission_type_id i.bounty_type_id 
local bounty_ctr_wo_cat project_difficulty_cont project_length_cont
local github_ctr lntotalownedbounties lnrepo_stars_count lnuser_public_repos lngithub_user_tenure lnorg_public_repos lngithub_owner_tenure 
local github_ctr lntotalownedbounties lnrepo_stars_count lnuser_public_repos lngithub_user_tenure

* Sampling
local if if project_type=="traditional"&comp_type!="fiat"&!mi(lnhourlyrate)&year>2017&permission_type_id==1
// local if if project_type!="cooperative"&comp_type!="fiat"&!mi(lnhourlyrate)&year>2017&permission_type_id==1

* Model config
local se r
local format rtf
// xtset org_name_id
local taboption ///
    nobase nogap noomit label star(* .1 ** .05 *** .01) drop(*bounty_type* *year*) ///
    refcat(project_difficulty_cont "Bounty characteristics:" lntotalownedbounties "Owner characteristics:", nolabel) ///
    nonote addnote(Note: Bounty categories and bounty year controlled. * p < .1, ** p < .05, *** p < .01)

* Table 1. Summary stats
sumtab `dvs' `ivs' `bounty_ctr_wo_cat' `github_ctr' `if', ///
    output("./result/table1_summary.`format'") title("Table 1. Summary statistics")

* Table 2. Regression
eststo clear
// eststo: nbreg num_interests `ivs' `owner_ctr' `bounty_ctr' `github_ctr' i.year `if', `se'
foreach dv in `participation' {
    eststo: reg `dv' `ivs' `owner_ctr' `bounty_ctr' `github_ctr' i.year `if', `se'
    // eststo: areg `dv' `ivs' `owner_ctr' `bounty_ctr' `github_ctr' i.year `if', absorb(org_name_id) `se'
    // eststo: reghdfe `dv' `ivs' `owner_ctr' `bounty_ctr' i.year `if', absorb(org_name_id) cluster(org_name_id year)
}
foreach iv in "`ivs'" "`ivs2'" {
    foreach dv in `performance' {
        eststo: logit `dv' `iv' `owner_ctr' `bounty_ctr' `github_ctr' i.year `if', `se'
    }
}
esttab using "./result/table2_regression.`format'", replace `taboption' ///
    order(lnvalue_in_usdt coin_stats_std_return *lnvalue_in_usdt*) ///
    title(Table 2. Regression on project performance)

// * Table 3. Performance
// eststo clear
// foreach iv in "`ivs'" "`ivs2'" {
//     foreach dv in `performance' {
//         eststo: logit `dv' lnnum_interests lnhourlyrate `iv' `owner_ctr' `bounty_ctr' `github_ctr' i.year `if', `se'
//     }
// }
// esttab using "./result/performance.`format'", replace `taboption' ///
//     stats(N ll, labels("Observations" "Log likelihood")) ///
//     order(lnvalue_in_usdt coin_stats_std_return *lnvalue_in_usdt*) ///
//     title(Table xx. Regression on bounty performance)

* Misc
tabstat value_in_usdt `if', by(value_cat)

* marginal effect
*** Figure 1. Predicted margins of alliance performance by IT specificity
set graph off
logit submitted `ivs2' `owner_ctr' `bounty_ctr' `github_ctr' i.year `if', `se'
margins, dydx(coin_stats_std_return) at(lnvalue_in_usdt=(0(1)10)) atmeans
marginsplot, title("") name(submitted, replace) 
logit accepted `ivs2' `owner_ctr' `bounty_ctr' `github_ctr' i.year `if', `se'
margins, dydx(coin_stats_std_return) at(lnvalue_in_usdt=(0(1)10)) atmeans
marginsplot, title("") name(accepted, replace) 
gr combine submitted accepted
graph export "./result/marginaleffect.png", replace
set graph on

distinct token_name `if'