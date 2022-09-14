cap prog drop get_para
prog get_para, rclass
	syntax, coln(string) line(string)

	while "`line'"!= "" {
	gettoken name coln : coln, parse(",")
	gettoken num line : line, parse(",")
		if "`name'"!="," & "`num'"!="," {
			return local `name' = "`num'"
		}
	}
end
