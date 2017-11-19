
def normalize_active_ingredients(data):
    """Normalizes the active ingredient entries"""
    normalized_data = []

    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "active_ingredient_code": item[1],
            "ingredient": item[2],
            "ingredient_supplied_ind": item[3],
            "strength": item[4],
            "strength_unit": item[5],
            "strength_type": item[6],
            "dosage_value": item[7],
            "base": item[8],
            "dosage_unit": item[9],
            "notes": item[10],
            "ingredient_f": item[11],
            "strength_unit_f": item[12],
            "strength_type_f": item[13],
            "dosage_unit_f": item[14],
        })

    return normalized_data
            
def normalize_companies(data):
    """Normalizes the companies entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "mfr_code": item[1],
            "company_code": item[2],
            "company_name": item[3],
            "company_type": item[4],
            "address_mailing_flag": item[5],
            "address_billing_flag": item[6],
            "address_notification_flag": item[7],
            "address_other": item[8],
            "suite_number": item[9],
            "street_name": item[10],
            "city_name": item[11],
            "province": item[12],
            "country": item[13],
            "postal_code": item[14],
            "post_office_box": item[15],
            "province_f": item[16],
            "country_f": item[17],
        })
    
    return normalized_data

def normalize_drug_product(data):
    """Normalizes the drug product entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "product_categorization": item[1],
            "class_": item[2],
            "brand_name": item[3],
            "descriptor": item[4],
            "pediatric_flag": item[5],
            "accession_number": item[6],
            "number_of_ais": item[7],
            "late_update_date": item[8],
            "ai_group_no": item[9],
            "class_f": item[10],
            "brand_name_f": item[11],
            "descriptor_f": item[12],
        })
    
    return normalized_data

def normalize_form(data):
    """Normalizes the form entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "pharm_form_code": item[1],
            "pharmaceutical_form": item[2],
            "pharmaceutical_form_f": item[3],
        })
    
    return normalized_data

def normalize_inactive_products(data):
    """Normalizes the inactive products entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "drug_identification_number": item[1],
            "brand_name": item[2],
            "history_date": item[3],
        })
    
    return normalized_data

def normalize_packaging(data):
    """Normalizes the packaging entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "upc": item[1],
            "package_size_unit": item[2],
            "package_type": item[3],
            "package_size": item[4],
            "product_information": item[5],
            "package_size_unit_f": item[6],
            "package_type_f": item[7],
        })
    
    return normalized_data

def normalize_pharmaceutical_standard(data):
    """Normalizes the pharmaceutical standard entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "pharmaceutical_std": item[1],
        })
    
    return normalized_data

def normalize_route(data):
    """Normalizes the route entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "route_of_administration_code": item[1],
            "route_of_administration": item[2],
            "route_of_administration_f": item[3],
        })
    
    return normalized_data

def normalize_schedule(data):
    """Normalizes the schedule entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "schedule": item[1],
            "schedule_f": item[2],
        })
    
    return normalized_data

def normalize_status(data):
    """Normalizes the status entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "current_status_flag": item[1],
            "status": item[2],
            "history_date": item[3],
            "status_f": item[4],
            "lot_number": item[5],
            "expiration_date": item[6],
        })
    
    return normalized_data

def normalize_therapeutic_class(data):
    """Normalizes the therapeutic class entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "tc_atc_number": item[1],
            "tc_atc": item[2],
            "tc_ahfs_number": item[3],
            "tc_ahfs": item[4],
            "tc_atc_f": item[5],
            "tc_ahfs_f": item[6],
        })
    
    return normalized_data

def normalize_veterinary_status(data):
    """Normalizes the veterinary status entries"""
    
    # Cycle through each entry
    for item in data:
        normalized_data.append({
            "drug_code": item[0],
            "vet_species": item[1],
            "vet_sub_species": item[2],
            "vet_species_f": item[3],
        })
    
    return normalized_data

def normalize_entries(data, model):
    """Normalizes the data based on the provided model"""
    # ActiveIngredient
    if model == "ActiveIngredients":
        normalized_data = normalize_active_ingredients(data)

    # Companies
    elif model == "Companies":
        normalized_data = normalize_companies(data)

    # DrugProduct
    elif model == "DrugProduct":
        normalized_data = normalize_drug_product(data)

    # Form
    elif model == "Form":
        normalized_data = normalize_form(data)
        
    # InactiveProducts
    elif model == "InactiveProducts":
        normalized_data = normalize_inactive_products(data)

    # Packaging
    elif model == "Packaging":
        normalized_data = normalize_packaging(data)

    # PharmaceuticalStandard
    elif model == "PharmaceuticalStandard":
        normalized_data = normalize_pharmaceutical_standard(data)

    # Route
    elif model == "Route":
        normalized_data = normalize_route(data)

    # Schedule
    elif model == "Schedule":
        normalized_data = normalize_schedule(data)

    # Status
    elif model == "Status":
        normalized_data = normalize_status(data)

    # TherapeuticClass
    elif model == "TherapeuticClass":
        normalized_data = normalize_therapeutic_class(data)

    # VeterinarySpecies
    elif model == "VeterinarySpecies":
        normalized_data = normalize_veterinary_status(data)

    return normalized_data

def normalize_data(dpd_data):
    """Normalizes the extracted dpd data"""
    # Cycle through each extension
    for extension_key, extension in data.items():
        # Cycle through each data file
        for file_key, file in extension.items():
            # Convert the data to a dictionary and normalize the entries
            file["data"] = normalize_entries(file["data"], file["model"])
    
    return dpd_data