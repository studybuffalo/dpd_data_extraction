def generate_query(name):
    """Generates a MySQL query for data insertion"""
    if name == "comp":
        output = (
            "INSERT INTO dpd_comp(drug_code, mfr_code, company_code, "
            "company_name, company_type, address_mailing_flag, "
            "address_billing_flag, address_notification_flag, address_other, "
            "suite_number, street_name, city_name, province, country, "
            "postal_code, post_office_box) values "
            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
    
    elif name == "drug":
        output = (
            "INSERT INTO dpd_drug(drug_code, product_categorization, class, "
            "drug_identification_number, brand_name, descriptor, "
            "pediatric_flag, accession_number, number_of_ais, "
            "last_update_date, ai_group_no) values "
            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
    
    elif name == "form":
        output = (
            "INSERT INTO dpd_form(drug_code, pharm_form_code, "
            "pharmaceutical_form) values (%s, %s, %s)"
        )
    
    elif name == "ingred":
        output = (
            "INSERT INTO dpd_ingred(drug_code, active_ingredient_code, "
            "ingredient, ingredient_supplied_ind, strength, strength_unit, "
            "strength_type, dosage_value, base, dosage_unit, notes) values "
		    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
    
    elif name == "package":
        output = (
            "INSERT INTO dpd_package(drug_code, upc, package_size_unit, "
            "package_type, package_size, product_information) values "
            "(%s, %s, %s, %s, %s, %s)"
        )
    
    elif name == "pharm":
        output = (
            "INSERT INTO dpd_pharm(drug_code, pharmaceutical_std) "
            "values (%s, %s)"
        )
    
    elif name == "route":
        output = (
            "INSERT INTO dpd_route(drug_code, route_of_administration_code, "
            "route_of_administration) values (%s, %s, %s)"
        )
    
    elif name == "schedule":
        output = (
            "INSERT INTO dpd_schedule(drug_code, schedule) values (%s, %s)"
        )
    
    elif name == "status":
        output = (
            "INSERT INTO dpd_status(drug_code, current_status_flag, status, "
            "history_date) values (%s, %s, %s, %s)"
        )
    
    elif name == "ther":
        output = (
            "INSERT INTO dpd_ther(drug_code, tc_atc_number, tc_atc, "
            "tc_ahfs_number, tc_ahfs) values (%s, %s, %s, %s, %s)"
        )
    
    elif name == "vet":
        output = (
            "INSERT INTO dpd_vet(drug_code, vet_species, vet_sub_species) "
            "values (%s, %s, %s)"
        )
    
    return output

def upload_to_table(cur, name, data):
    """Truncates old table and uploads new table data"""
    # Truncate old data from table
    query = "TRUNCATE dpd_%s" % name
    cur.execute(query)

    # Upload new data to table
    query = generate_query(name)
    cur.executemany(query, data)