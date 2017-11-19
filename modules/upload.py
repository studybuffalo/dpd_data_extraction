import logging



# Setup logging
log = logging.getLogger(__name__)


def save_to_model(item, model_name, origin):
    """Saves the provide item to the specified model"""
    
    # Import the model references
    from hc_dpd.models import (
        DPD, ActiveIngredients, Companies, DrugProduct, Form, 
        InactiveProducts, Packaging, PharmaceuticalStandard, Route, 
        Schedule, Status, TherapeuticClass, VeterinarySpecies, 
    )

    # Turn off the query logging
    logging.getLogger("django.db.backends").setLevel(logging.CRITICAL)

    # Create an entry in the DPD model or retrieve the item
    dpd_entry, _ = DPD.objects.get_or_create(drug_code=item["drug_code"])

    # Add/update the origin_file if needed
    if dpd_entry.origin_file != origin:
        dpd_entry.origin_file = origin
        dpd_entry.save()

    # Upload the data with the associated dpd_entry to the proper model
    # ActiveIngredient
    if model_name == "ActiveIngredients":
        model = ActiveIngredients(
            drug_code=dpd_entry,
            active_ingredient_code=item["active_ingredient_code"],
            ingredient=item["ingredient"],
            ingredient_supplied_ind=item["ingredient_supplied_ind"],
            strength=item["strength"],
            strength_unit=item["strength_unit"],
            strength_type=item["strength_type"],
            dosage_value=item["dosage_value"],
            base=item["base"],
            dosage_unit=item["dosage_unit"],
            notes=item["notes"],
            ingredient_f=item["ingredient_f"],
            strength_unit_f=item["strength_unit_f"],
            strength_type_f=item["strength_type_f"],
            dosage_unit_f=item["dosage_unit_f"],
        )
        model.save()

    # Companies
    elif model_name == "Companies":
        model = Companies(
            drug_code=dpd_entry,
            mfr_code=item["mfr_code"],
            company_code=item["company_code"],
            company_name=item["company_name"],
            company_type=item["company_type"],
            address_mailing_flag=item["address_mailing_flag"],
            address_billing_flag=item["address_billing_flag"],
            address_notification_flag=item["address_notification_flag"],
            address_other=item["address_other"],
            suite_number=item["suite_number"],
            street_name=item["street_name"],
            city_name=item["city_name"],
            province=item["province"],
            country=item["country"],
            postal_code=item["postal_code"],
            post_office_box=item["post_office_box"],
            province_f=item["province_f"],
            country_f=item["country_f"],
        )
        model.save()

    # DrugProduct
    elif model_name == "DrugProduct":
        model = DrugProduct(
            drug_code=dpd_entry,
            product_categorization=item["product_categorization"],
            class_e=item["class_e"],
            drug_identification_number=item["drug_identification_number"],
            brand_name=item["brand_name"],
            descriptor=item["descriptor"],
            pediatric_flag=item["pediatric_flag"],
            accession_number=item["accession_number"],
            number_of_ais=item["number_of_ais"],
            late_update_date=item["late_update_date"],
            ai_group_no=item["ai_group_no"],
            class_f=item["class_f"],
            brand_name_f=item["brand_name_f"],
            descriptor_f=item["descriptor_f"],
        )
        model.save()

    # Form
    elif model_name == "Form":
        model = Form(
            drug_code=dpd_entry,
            pharm_form_code=item["pharm_form_code"],
            pharmaceutical_form=item["pharmaceutical_form"],
            pharmaceutical_form_f=item["pharmaceutical_form_f"],
        )
        model.save()
        
    # InactiveProducts
    elif model_name == "InactiveProducts":
        model = InactiveProducts(
            drug_code=dpd_entry,
            drug_identification_number=item["drug_identification_number"],
            brand_name=item["brand_name"],
            history_date=item["history_date"],
        )
        model.save()

    # Packaging
    elif model_name == "Packaging":
        model = Packaging(
            drug_code=dpd_entry,
            upc=item["upc"],
            package_size_unit=item["package_size_unit"],
            package_type=item["package_type"],
            package_size=item["package_size"],
            product_information=item["product_information"],
            package_size_unit_f=item["package_size_unit_f"],
            package_type_f=item["package_type_f"],
        )
        model.save()

    # PharmaceuticalStandard
    elif model_name == "PharmaceuticalStandard":
        model = PharmaceuticalStandard(
            drug_code=dpd_entry,
            pharmaceutical_std=item["pharmaceutical_std"],
        )
        model.save()

    # Route
    elif model_name == "Route":
        model = Route(
            drug_code=dpd_entry,
            route_of_administration_code=item["route_of_administration_code"],
            route_of_administration=item["route_of_administration"],
            route_of_administration_f=item["route_of_administration_f"],
        )
        model.save()

    # Schedule
    elif model_name == "Schedule":
        model = Schedule(
            drug_code=dpd_entry,
            schedule=item["schedule"],
            schedule_f=item["schedule_f"],
        )
        model.save()

    # Status
    elif model_name == "Status":
        model = Status(
            drug_code=dpd_entry,
            current_status_flag=item["current_status_flag"],
            status=item["status"],
            history_date=item["history_date"],
            status_f=item["status_f"],
            lot_number=item["lot_number"],
            expiration_date=item["expiration_date"],
        )
        model.save()

    # TherapeuticClass
    elif model_name == "TherapeuticClass":
        model = TherapeuticClass(
            drug_code=dpd_entry,
            tc_atc_number=item["tc_atc_number"],
            tc_atc=item["tc_atc"],
            tc_ahfs_number=item["tc_ahfs_number"],
            tc_ahfs=item["tc_ahfs"],
            tc_atc_f=item["tc_atc_f"],
            tc_ahfs_f=item["tc_ahfs_f"],
        )
        model.save()

    # VeterinarySpecies
    elif model_name == "VeterinarySpecies":
        model = VeterinarySpecies(
            drug_code=dpd_entry,
            vet_species=item["vet_species"],
            vet_sub_species=item["vet_sub_species"],
            vet_species_f=item["vet_species_f"],
        )
        model.save()
    
def upload_data(config, data):
    """Uploads normalized data to the Django database"""
   

    # Cycle through each extension
    for extension_key, extension in data.items():
        log.debug("Uploading {} files".format(extension_key))

        # Cycle through each data file
        for file_key, file in extension.items():
            # Get the model and origin data
            django_model = file["model"]
            django_origin = file["origin"]

            log.debug("Uploading to the {} model".format(django_model))

            # Cycle through each extract item and upload it
            for item in file["data"]:
                save_to_model(item, django_model, django_origin)