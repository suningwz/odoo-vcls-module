# -*- coding: utf-8 -*-

###############################
# PAYROLL EXPORT FILE HEADERS #
###############################

PAYROLL_FR_V1 = [
                {'h_name': 'ID','field_name': 'employee_external_id'},
                {'h_name': 'Année','field_name': 'year'},
                {'h_name': 'Mois','field_name': 'month'},
                {'h_name': 'Date virement','field_name': 'payment_date'},
                {'h_name': 'Location','field_name': 'location'},
                {'h_name': 'Prénom','field_name': 'first_name'},
                {'h_name': 'Nom','field_name': 'family_name'},
                {'h_name': 'Contrat','field_name': 'contract_type'},
                {'h_name': 'Temps travail','field_name': 'working_percentage'},
                {'h_name': 'Statut','field_name': 'status'},
                {'h_name': 'Salaire_100','field_name': 'fulltime_salary'},
                {'h_name': 'Salaire_prorata','field_name': 'prorated_salary'},
                {'h_name': 'Bonus','field_name': 'total_bonus'},
                {'h_name': 'Avantage nature','field_name': 'car_allowance'},
                {'h_name': 'Transport','field_name': 'transport_allowance'},
                {'h_name': 'Tickets resto','field_name': 'lunch_ticket'},
                {'h_name': 'RTT pris','field_name': 'rtt_paid_days'},
                {'h_name': 'Info RTT pris','field_name': 'rtt_paid_info'},
                {'h_name': 'CP pris','field_name': 'cp_paid_days'},
                {'h_name': 'Info CP pris','field_name': 'cp_paid_info'},
                {'h_name': 'CP sans solde','field_name': 'cp_unpaid_days'},
                {'h_name': 'Info CP sans solde','field_name': 'cp_unpaid_info'},
                {'h_name': 'Maladie','field_name': 'sick_days'},
                {'h_name': 'Info Maladie','field_name': 'sick_info'},
                {'h_name': 'Absence exc.','field_name': 'other_paid_days'},
                {'h_name': 'Info Absence exc.','field_name': 'other_paid_info'},
                {'h_name': 'Commentaires','field_name': 'comments'},
            ]