class AccountOfficerStatement:

    def __init__(self, start_date=None, end_date=None, branch_code=None,
                 social_number=None, personnel_id=None, phone_number=None):
        self.start_date = start_date
        self.end_date = end_date
        self.branch_code = branch_code
        self.social_number = social_number
        self.personnel_id = personnel_id
        self.phone_number = phone_number
        self.branch_score_condition = "WHERE BRANCH_CODE = '{}'"\
            .format(self.branch_code) if self.branch_code else ""
        self.weak_score_condition = "AND customer.BRANCH_CODE = '{}'"\
            .format(self.branch_code) if self.branch_code else ""
        self.customer_search_condition = (
            "and (officers.PERSONNEL_ID= '{}'"
            " or officers.SSN = '{}' or officers.CELL_PHONE_NO = '{}' or officers.branch_code = '{}')"
            .format(self.personnel_id, self.social_number, self.phone_number, self.branch_code) if \
            self.social_number or self.personnel_id or self.phone_number or self.branch_code else ""
        )
        self.officer_search_condition = (
            "and (supervisors.PERSONNEL_ID= '{}'"
            " or supervisors.SSN = '{}' or supervisors.CELL_PHONE_NO = '{}' or officers.branch_code = '{}')"
                .format(self.personnel_id, self.social_number, self.phone_number, self.branch_code) if \
                self.social_number or self.personnel_id or self.phone_number or self.branch_code else ""
        )
        self.supervisor_search_condition = (
            "and (supervisors.PERSONNEL_ID = '{}'"
            " or supervisors.SSN = '{}' or supervisors.CELL_PHONE_NO = '{}' or supervisors.branch_code = '{}')"
                .format(self.personnel_id, self.social_number, self.phone_number, self.branch_code) if \
                self.social_number or self.personnel_id or self.phone_number or self.branch_code else ""
        )

        self.calculated_score_part = (
            'SUM(CASE WHEN request.REQ_COUNT <= 2 '
            'THEN ROUND(REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE)'
            'WHEN REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE * 0.7 > 200 '
            'THEN 200 '
            'ELSE ROUND(REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE * 0.7) '
            'END )'
        )
        self.request_score_part = (
            "(SELECT request.id as request_id ,request.SERVICE_ID," 
            "{} as total_score, SUM(request.REQ_COUNT) as request_count,"
            "request.ASSIGN_ID as assign_id"
            " FROM ACC_OFF.REQUESTS as request" 
            " join ACC_OFF.SCORES scores" 
            " ON request.ID = scores.REQUEST_ID" 
            " AND request.creation_date > '{}'" 
            " AND request.creation_date <'{}'" 
            " GROUP BY request.ID, request.SERVICE_ID, assign_id) request_score"
                .format(
                    self.calculated_score_part,
                    start_date,
                    end_date,
                )
        )

        self.service_score_statement = (
            "SELECT services.DESCRIPTION as service,"
            " category.DESCTIPION as category," 
            " SUM(request_score.total_score) as score,"
            " SUM(request_count) as request_count" 
            " FROM {}"
            " join ACC_OFF.SERVICES services" 
            " JOIN ACC_OFF.SERVICE_CATEGORIES category" 
            " ON services.CATEGOTY_ID = category.ID" 
            " ON services.id = request_score.SERVICE_ID" 
            " GROUP BY services.DESCRIPTION, category.DESCTIPION"
                .format(self.request_score_part)
        )

        self.branch_scores_statement = (
            "SELECT BRANCH_CODE, BRANCH_NAME, service, category,"
            " SUM(score) as score, SUM(request_count) as request_count"
            " FROM (SELECT officer.BRANCH_CODE, officer.BRANCH_NAME,"
            " assing.id as assign_id"
            " FROM ACC_OFF.ACCOUNT_OFFICERS officer"
            " JOIN ACC_OFF.ASSIGNS assing"
            " ON officer.ID = assing.OFFICER_ID) officers_assign"
            " JOIN (SELECT services.DESCRIPTION as service,"
            " category.DESCTIPION as category,"
            " SUM(request_score.total_score) as score,"
            " SUM(request_score.request_count) as request_count,"
            " assign_id"
            " FROM {}"
            " join ACC_OFF.SERVICES services"
            " JOIN ACC_OFF.SERVICE_CATEGORIES category"
            " ON services.CATEGOTY_ID = category.ID"
            " ON services.id = request_score.SERVICE_ID"
            " GROUP BY services.DESCRIPTION, category.DESCTIPION, assign_id)"
            " service_socre"
            " ON officers_assign.assign_id = service_socre.assign_id"
            " {}"
            " GROUP BY BRANCH_CODE, BRANCH_NAME, service, category"
                .format(self.request_score_part, self.branch_score_condition)
        )

        self.branch_request_statement = (
            "SELECT BRANCH_CODE, sum(REQ_COUNT) as request_count"
            " FROM (SELECT BRANCH_NAME, BRANCH_CODE, assign.id"
            " FROM ACC_OFF.ACCOUNT_OFFICERS officers"
            " join ACC_OFF.ASSIGNS assign"
            " ON officers.ID = assign.OFFICER_ID) officer_assign"
            " JOIN ACC_OFF.REQUESTS request"
            " ON request.ASSIGN_ID = officer_assign.ID"
            " AND request.creation_date > '{}'"
            " AND request.creation_date < '{}'"
            " GROUP BY BRANCH_CODE".format(self.start_date, self.end_date)
        )

        self.officers_score_statement = (
           "SELECT offcier_request_score.NAME, FAMILY, PERSONNEL_ID,"
           " BRANCH_CODE, SUM(CASE WHEN SHARE_PERCENTAGE is NULL THEN scores"
           " ELSE scores * (1-(SHARE_PERCENTAGE / 100.0)) END ) as score"
           " FROM (SELECT officer.name, officer.FAMILY, officer.PERSONNEL_ID,"
           " BRANCH_CODE, request.id as request_id,"
           " SUM(CASE WHEN request.REQ_COUNT <= 2"
           "  THEN REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE"
           " WHEN REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE * 0.7 > 200"
           "  THEN 200"
           "  ELSE REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE * 0.7"
           " END ) as scores  FROM ACC_OFF.ACCOUNT_OFFICERS officer"
           " JOIN ACC_OFF.ASSIGNS assign on officer.ID = assign.OFFICER_ID"
           " JOIN ACC_OFF.REQUESTS request ON assign.ID = request.ASSIGN_ID"
           "  JOIN ACC_OFF.SCORES score ON request.ID = score.REQUEST_ID"
           "  and score.ISSUE_DATE > '{}'"
           " and score.ISSUE_DATE < '{}'"
           " GROUP BY officer.name, officer.FAMILY, officer.PERSONNEL_ID,"
           " officer.BRANCH_CODE, request.id) offcier_request_score"
           " left join ACC_OFF.PARTICIPANTS participants"
           " ON offcier_request_score.request_id = participants.REQUEST_ID"
           " GROUP BY NAME, FAMILY, PERSONNEL_ID, BRANCH_CODE;".format(
               self.start_date,
               self.end_date
           )
        )

        self.collaborators_score_statement = (
           "SELECT distinct collaborator_score.*, employee.BRANCH_CODE"
           " FROM ACC_OFF.EMPLOYEES employee"
           " join (select name, FAMILY, PERSONNEL_ID,"
           " sum((SHARE_PERCENTAGE / 100.0) * score) as score"
           " FROM (select participants.REQUEST_ID, NAME, FAMILY, PERSONNEL_ID,"
           " participants.SHARE_PERCENTAGE"
           " from ACC_OFF.PARTNERS partner"
           " join ACC_OFF.PARTICIPANTS participants"
           " on partner.ID = participants.PARTNER_ID) partner_participant"
           " join (SELECT request.id as request_id,"
           " SUM(CASE WHEN request.REQ_COUNT <= 2"
           "  THEN ROUND(REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE)"
           " WHEN REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE * 0.7 > 200"
           "  THEN 200"
           "  ELSE ROUND(REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE * 0.7)"
           " END ) as score FROM ACC_OFF.REQUESTS request"
           " join ACC_OFF.SCORES score on request.ID = score.REQUEST_ID"
           " and score.ISSUE_DATE > '{}'"
           " and score.ISSUE_DATE < '{}'"
           " group by request.ID) request_score"
           " on partner_participant.REQUEST_ID = request_score.request_id"
           " GROUP BY name, family, personnel_id)collaborator_score"
           " on employee.PERSONNEL_ID = collaborator_score.PERSONNEL_ID;"\
               .format(self.start_date, self.end_date)
        )

        self.supervisor_score_statement = (
            "SELECT name, FAMILY, PERSONNEL_ID, BRANCH_CODE,"
            " supervisorscore.score"
            " FROM ACC_OFF.ACCOUNT_OFFICERS officer"
            " join (SELECT supervisor_id,"
            " (CAST(sum(supervisor.score)"
            " as FLOAT)/count(supervisor.PERSONNEL_ID)) as score"
            " from (SELECT offcier_request_score.NAME, FAMILY,"
            " PERSONNEL_ID,supervisor_id,"
            " SUM(CASE WHEN SHARE_PERCENTAGE is NULL THEN scores"
            " ELSE scores * (1-(SHARE_PERCENTAGE / 100.0)) END ) as score"
            " FROM (SELECT officer.name, officer.FAMILY, officer.PERSONNEL_ID,"
            " officer.SUPERVISOR_ID as supervisor_id, request.id as request_id,"
            " SUM(CASE WHEN request.REQ_COUNT <= 2"
            "  THEN REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE"
            " WHEN REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE * 0.7 > 200"
            "  THEN 200"
            "  ELSE REQ_COUNT * VALUE * SERVICE_COMPLEXITY_VALUE * 0.7"
            " END ) as scores  FROM ACC_OFF.ACCOUNT_OFFICERS officer"
            " JOIN ACC_OFF.ASSIGNS assign on officer.ID = assign.OFFICER_ID"
            " JOIN ACC_OFF.REQUESTS request ON assign.ID = request.ASSIGN_ID"
            "  JOIN ACC_OFF.SCORES score ON request.ID = score.REQUEST_ID"
            "  and score.ISSUE_DATE > '{}'"
            " and score.ISSUE_DATE < '{}'"
            " GROUP BY officer.name, officer.FAMILY, officer.PERSONNEL_ID,"
            " officer.supervisor_id, request.id) offcier_request_score"
            " left join ACC_OFF.PARTICIPANTS participants"
            " ON offcier_request_score.request_id = participants.REQUEST_ID"
            " GROUP BY NAME, FAMILY, PERSONNEL_ID, supervisor_id)supervisor"
            " GROUP BY supervisor.supervisor_id)supervisorscore"
            " on supervisorscore.supervisor_id = officer.ID;".format(
                self.start_date,
                self.end_date
            )
        )

        self.weak_score_statement = (
            "SELECT  customer.NAME as costomer_name,"
            " customer.FAMILY as costomer_family, customer.CELL_PHONE_NO,"
            " officers.name, officers.FAMILY, services.DESCRIPTION,"
            " score.COMMENT, score.VALUE"
            " FROM ACC_OFF.ACCOUNT_OFFICERS officers"
            " join ACC_OFF.ASSIGNS assign"
            " on officers.ID = assign.OFFICER_ID"
            " join ACC_OFF.VIP_CUSTOMER customer"
            " on assign.CUSTOMER_ID = customer.ID"
            " join ACC_OFF.REQUESTS request on"
            " assign.ID = request.ASSIGN_ID"
            " join ACC_OFF.SERVICES services"
            " on request.SERVICE_ID = services.ID"
            " join ACC_OFF.SCORES score"
            " on request.ID = score.REQUEST_ID"
            " AND score.ISSUE_DATE > '{}'"
            "  AND  score.ISSUE_DATE< '{}'"
            " where score.VALUE < 3"
            " {};".format(
                self.start_date,
                self.end_date,
                self.weak_score_condition
            )
        )

        self.customer_search_statement = (
            "SELECT officers.name as officer_name,"
            " officers.FAMILY as officer_family,"
            " officers.SSN as officer_social_number, officers.PERSONNEL_ID,"
            " officers.BRANCH_CODE, officers.BRANCH_NAME,"
            " customer.name, customer.family, customer.CELL_PHONE_NO,"
            " customer.SSN,"
            " customer.STATUS, customer.TYPE"
            " FROM (SELECT customer.name, customer.FAMILY,"
            " customer.CELL_PHONE_NO, customer.SSN,"
            " customer.STATUS, customer.ID, customer.TYPE,"
            "  MAX(ASSIGN_DATE) as assing_date, customer.CREATION_DATE"
            " FROM ACC_OFF.VIP_CUSTOMER customer"
            " join ACC_OFF.ASSIGNS assign"
            " ON customer.ID = assign.CUSTOMER_ID"
            " GROUP BY customer.NAME, customer.FAMILY, customer.id,"
            " cell_phone_no, family, name, ssn, type, status, CREATION_DATE)"
            " customer"
            " JOIN ACC_OFF.ASSIGNS assign ON assign.CUSTOMER_ID = customer.ID"
            " and customer.assing_date = assign.ASSIGN_DATE"
            " JOIN ACC_OFF.ACCOUNT_OFFICERS officers"
            " ON assign.OFFICER_ID = officers.ID"
            " WHERE customer.CREATION_DATE between '{}'"
            " and '{}'"
            " {};".format(self.start_date, self.end_date, self.customer_search_condition)
        )

        self.officer_search_statement = (
            "SELECT supervisors.SSN as supervisor_social_number,"
            " supervisors.personnel_id as supervisor_personnel_id,"
            " supervisors.name as supervisor_name,"
            " supervisors.family as supervisor_family,"
            " officers.type,"
            " officers.name, officers.family, officers.ssn,"
            " officers.cell_phone_no, officers.personnel_id,"
            " officers.branch_code, officers.branch_name, officers.status"
            " FROM"
            " (SELECT * FROM ACC_OFF.ACCOUNT_OFFICERS officers"
            " WHERE officers.id in (SELECT SUPERVISOR_ID"
            " from ACC_OFF.ACCOUNT_OFFICERS officers) )supervisors"
            " right join  ACC_OFF.ACCOUNT_OFFICERS officers"
            " on supervisors.id = officers.SUPERVISOR_ID"
            " where officers.CREATION_DATE"
            " between '{}'"
            " and '{}'"
            " {};".format(
                self.start_date,
                self.end_date,
                self.officer_search_condition
            )
        )

        self.supervisor_search_statement = (
            "SELECT name, family, personnel_id, ssn, cell_phone_no,"
            " branch_code, branch_name, status"
            " FROM ACC_OFF.ACCOUNT_OFFICERS supervisors"
            " where supervisors.id in"
            " (SELECT SUPERVISOR_ID FROM ACC_OFF.ACCOUNT_OFFICERS officers)"
            " {};".format(self.supervisor_search_condition)
        )

