# -*- coding: latin-1 -*-
from MySQLdb import escape_string

def generate_statement(table):
	output = "INSERT INTO `%s`" % table
	
	if table == "comp" or table == "comp_ia" or table == "comp_ap":
		output += ("(`drug_code`,`mfr_code`,"
				   "`company_code`,`company_name`,`company_type`,"
				   "`address_mailing_flag`,`address_billing_flag`,"
				   "`address_notification_flag`,`address_other`,"
				   "`suite_number`,`street_name`,`city_name`,"
				   "`province`,`country`,`postal_code`,"
				   "`post_office_box`) values "
				   "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
	
	elif table == "drug" or table == "drug_ia" or table == "drug_ap":
		output += ("(`drug_code`, "
				   "`product_categorization`,`class`, "
				   "`drug_identification_number`,`brand_name`,"
				   "`descriptor`,`pediatric_flag`,`accession_number`,"
				   "`number_of_ais`,`last_update_date`,"
				   "`ai_group_no`) values "
				   "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
	
	elif table == "form" or  table == "form_ia" or  table == "form_ap":
		output += ("(`drug_code`,`pharm_form_code`,"
				   "`pharmaceutical_form`) values (%s,%s,%s)")
	
	elif table == "ingred" or  table == "ingred_ia" or  table == "ingred_ap":
		output += ("(`drug_code`,"
				   "`active_ingredient_code`,`ingredient`,"
				   "`ingredient_supplied_ind`,`strength`,"
				   "`strength_unit`,`strength_type`,"
				   "`dosage_value`,`base`,`dosage_unit`,"
				   "`notes`) values "
				   "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
	
	elif table == "package" or table == "package_ia" or  table == "package_ap":
		output += ("(`drug_code`,`upc`,"
				   "`package_size_unit`,`package_type`,"
				   "`package_size`,`product information`) values "
				   "(%s,%s,%s,%s,%s,%s)")
	
	elif table == "pharm" or  table == "pharm_ia" or  table == "pharm_ap":
		output += ("(`drug_code`,"
				   "`pharmaceutical_std`) values (%s,%s)")
	
	elif table == "route" or  table == "route_ia" or  table == "route_ap":
		output += ("(`drug_code`,"
				   "`route_of_administration_code`,"
				   "`route_of_administration`) values "
				   "(%s,%s,%s)")
	
	elif table == "schedule" or  table == "schedule_ia" or  table == "schedule_ap":
		output += ("(`drug_code`,`schedule`) values "
				   "(%s,%s)")
	
	elif table == "status" or  table == "status_ia" or  table == "status_ap":
		output += ("(`drug_code`,"
				   "`current_status_flag`,`status`,"
				   "`history_date`) values "
				   "(%s,%s,%s,%s)")
	
	elif table == "ther" or  table == "ther_ia" or  table == "ther_ap":
		output += ("(`drug_code`,`tc_atc_number`,"
				   "`tc_atc`,`tc_ahfs_number`,"
				   "`tc_ahfs`) values "
				   "(%s,%s,%s,%s,%s)")
	
	elif table == "vet" or  table == "vet_ia" or  table == "vet_ap":
		output += ("(`drug_code`,`vet_species`,"
				   "`vet_sub_species`) values (%s,%s,%s)")
	
	else:
		print("Error - %s not found" % table)
		
	return output
	
def generate_upload(table, line):
	"""Prepares the .txt line for MySQL insertion
	
	Takes a single line from a parsed text file and prepares it for 
	insertion into a MySQL database.
	
	Args:
		table: the table name in which the string will be inserted
		line: the line of text to be inserted.
	
	Returns:
		returns a string suitable for MySQL insertion.
		
	Raises:
		None.
	"""
	
	line = line.encode('latin-1')
	text = line.split('","')
	output = ""
	
	if table == "comp" or table == "comp_ia" or table == "comp_ap":
		text[0] = text[0][1:]
		text[15] = text[15][:-2]
		
		output = (escape_string(text[0]), escape_string(text[1]),
				  escape_string(text[2]),escape_string(text[3]),
				  escape_string(text[4]),escape_string(text[5]),
				  escape_string(text[6]),escape_string(text[7]),
				  escape_string(text[8]),escape_string(text[9]),
				  escape_string(text[10]),escape_string(text[11]),
				  escape_string(text[12]),escape_string(text[13]),
				  escape_string(text[14]),escape_string(text[15]))
	
	elif table == "drug" or table == "drug_ia" or table == "drug_ap":
		text[0] = text[0][1:]
		text[10] = text[10][:-2]
	
		output = (escape_string(text[0]),escape_string(text[1]),
				  escape_string(text[2]),escape_string(text[3]),
				  escape_string(text[4]),escape_string(text[5]),
				  escape_string(text[6]),escape_string(text[7]),
				  escape_string(text[8]),escape_string(text[9]),
				  escape_string(text[10]))
	
	elif table == "form" or  table == "form_ia" or  table == "form_ap":
		text[0] = text[0][1:]
		text[2] = text[2][:-2]
		
		output = (escape_string(text[0]),escape_string(text[1]),
				  escape_string(text[2]))
	
	elif table == "ingred" or  table == "ingred_ia" or  table == "ingred_ap":
		text[0] = text[0][1:]
		text[10] = text[10][:-2]
		
		output = (escape_string(text[0]),escape_string(text[1]),
				  escape_string(text[2]),escape_string(text[3]),
				  escape_string(text[4]),escape_string(text[5]),
				  escape_string(text[6]),escape_string(text[7]),
				  escape_string(text[8]),escape_string(text[9]),
				  escape_string(text[10]))
	
	elif table == "package" or table == "package_ia" or  table == "package_ap":
		text[0] = text[0][1:]
		text[5] = text[5][:-2]
		
		output = (escape_string(text[0]),escape_string(text[1]),
				  escape_string(text[2]),escape_string(text[3]),
				  escape_string(text[4]),escape_string(text[5]))
	
	elif table == "pharm" or  table == "pharm_ia" or  table == "pharm_ap":
		text[0] = text[0][1:]
		text[1] = text[1][:-2]
		
		output = (escape_string(text[0]),escape_string(text[1]))
	
	elif table == "route" or  table == "route_ia" or  table == "route_ap":
		text[0] = text[0][1:]
		text[2] = text[2][:-2]
		output = (escape_string(text[0]),escape_string(text[1]),
				  escape_string(text[2]))
	
	elif table == "schedule" or  table == "schedule_ia" or  table == "schedule_ap":
		text[0] = text[0][1:]
		text[1] = text[1][:-2]
		
		output = (escape_string(text[0]),escape_string(text[1]))
	
	elif table == "status" or  table == "status_ia" or  table == "status_ap":
		text[0] = text[0][1:]
		text[3] = text[3][:-2]
		
		output = (escape_string(text[0]),escape_string(text[1]),
				  escape_string(text[2]),escape_string(text[3]))
	
	elif table == "ther" or  table == "ther_ia" or  table == "ther_ap":
		text[0] = text[0][1:]
		text[4] = text[4][:-2]
		
		output = (escape_string(text[0]),escape_string(text[1]),
				  escape_string(text[2]),escape_string(text[3]),
				  escape_string(text[4]))
	
	elif table == "vet" or  table == "vet_ia" or  table == "vet_ap":
		text[0] = text[0][1:]
		text[2] = text[2][:-2]
		
		output = (escape_string(text[0]),escape_string(text[1]),
				  escape_string(text[2]))
	
	else:
		print("Error - %s not found" % table)
		
	return output