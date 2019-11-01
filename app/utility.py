# Helper functions

# takes a list, key, and query
def get_list(toFilterList, key, query):
	i = 0
	l = []
	while i < len(toFilterList):
		if toFilterList[i][key] == query:
			l.append(toFilterList[i])
		i += 1
	return l

# takes a cursor object, key, subkey and query
def get_cursor(cursor_obj, key, subkey, subkey2, query, query2):
	i = 0
	l = []
	while i < cursor_obj.count():
		j = 0
		while j < len(cursor_obj[i][key]):
			if cursor_obj[i][key][j][subkey] == query and cursor_obj[i][key][j][subkey2] == query2:
				l.append(cursor_obj[i])
			j += 1
		i += 1
	return l
		
# return index
def get_index(arrayList, key, query, key2, query2):
	i = 0
	while i < len(arrayList):
		print(arrayList[i][key])
		print(query)
		if arrayList[i][key] == query and arrayList[i][key2] == query2:
			return i
		i += 1
	return -1