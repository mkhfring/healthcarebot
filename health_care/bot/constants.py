class ConstantMessage:

    invalid_input = (
        'مقدار دریافتی اشتباه است، دوباره مقدار مورد نظر را وارد کنید:'
                     )
    branch_selection_message = (
        'کد شعبه ی مورد نظر را *وارد* '
        'و یا تمام شعب را *انتخاب* کنید:'
    )
    invalid_branch_code =(
        'کد *شعبه* اشتباه وارد شده است.'
        'لطفا دوباره کد شعبه را وارد نمایید.'
    )
    report_begin_date_message = (
        'لطفا *تاریخ شروع گزارش* '
        'یا *بازه گزارش (به چند روز قبل)* را مشخص نمایید:\n'
        'مثال: 970402 یا 3-5'
                                 )
    service_report_end_date = 'لطفا *تاریخ پایان گزارش* را وارد کنید:'
    bad_format = 'الگوی ورودی صحیح نیست.'
    menu_message = 'لطفا از میان گزینه های زیر انتخاب نمایید:'
    not_registered_message = 'متاسفانه شما در بازو ثبت نام نشده اید'
    customer_search_criterion = 'کد شعبه، کد پرسنلی، کد ملی یا شماره همراه بانک آفیسر مورد نظر را *وارد* و یا تمام بانک آفیسرها را *انتخاب* کنید:'
    officer_search_criterion = 'کد شعبه، کد پرسنلی، کد ملی یا شماره همراه ناظر مورد نظر را *وارد* و یا تمام بانک آفیسرها را *انتخاب* کنید:'


class ButtonMessage:
    service_report_message = 'گزارش امتیاز و خدمات'
    weak_score_report_message = 'گزارش امتیازات ضعیف'
    main_menu_message = 'بازگشت به منوی اصلی'
    all_branches = 'تمام شعب'
    all_officers = 'تمام بانک آفیسرها'
    officer_score_message = 'گزارش امتیاز اکانت آفیسرها، ناظرین و همکاران'
    customer_search_message = 'جستجوی مشتریان'
    officer_search_message = 'جستجوی اکانت آفیسر'
    supervisor_search_message = 'جستجوی ناظرین'


class RegexPattern:
    interval_pattern = r'\d+-\d+'
    monthandday_pattern = (
        '(1229|0[1-9]0[1-9]|0[1-9][1-2][0-9]|0[1-6]3[0-1]|0[7-9]30|1[0-1]0[1-9]'
        '|12[0][1-9]|12[1-2][0-9]|1[0-1][1-2][0-9]|1130|1030)$'
    )
    year_pattern = '^(9[0-9]|0[0-9])'
    jalali_input_pattern = year_pattern + monthandday_pattern
    branch_code_pattern = r'\d{1,4}$'
    national_id_pattern = r'\d{10}$'
    phone_number_pattern = r'989\d{9}$'


class FieldTranslation:

    CSV_FIELDS = {
        'title': 'عنوان درخواست', 'name': 'نام',
        'family': 'نام خانوادگی', 'shoab_code': 'کد شعبه',
        'shoab': 'نام شعبه', 'score': 'امتیاز',
        'request_count': 'تعداد درخواست'
    }

    SERVICE_SCORE_FIELDS = ['category', 'title', 'request_count', 'score']

    BRANCH_SCORE_FIELDS = [
        'branch_code',
        'branch_name',
        'category',
        'title',
        'request_count',
        'score'
    ]

    SERVICE_SCORE_TRANSLATION = {
        'CATEGORY': 'دسته خدمت',
        'SERVICE': 'عنوان خدمت',
        'REQUEST_COUNT': 'تعداد درخواست',
        'SCORE': 'امتیاز'
    }

    BRANCH_SCORE_TRANSLATION = {
        'BRANCH_CODE': 'کد شعبه',
        'BRANCH_NAME': 'نام شعبه',
        'CATEGORY': 'دسته خدمت',
        'SERVICE': 'عنوان خدمت',
        'REQUEST_COUNT': 'تعداد درخواست',
        'SCORE': 'امتیاز',
        'operation_unit': 'کد امور شعب'
    }

    BRANCH_REQUEST_TRANSLATIOM = {
        'BRANCH_CODE': 'کد شعبه',
        'REQUEST_COUNT': 'تعداد درخواست'
    }

    OFFICER_SCORE_TRANSLATION = {
        'NAME': 'نام',
        'FAMILY': 'نام خانوادگی',
        'PERSONNEL_ID': 'کد پرسنلی',
        'SCORE': 'امتیاز',
        'BRANCH_CODE': 'کد شعبه'
    }

    WEAK_SCORE_TRANSLATION = {
        'NAME': 'نام مدیر',
        'FAMILY': 'نام خانوادگی مدیر',
        'COSTOMER_NAME': 'نام خانوادگی مشتری',
        'COSTOMER_FAMILY': 'نام مشتری',
        'CELL_PHONE_NO': 'شماره تلفن مشتری',
        'DESCRIPTION': 'نام خدمت',
        'VALUE': 'امتیاز کسب شده',
        'COMMENT': 'توضیحات'
    }

    CUSTOMER_SEARCH_TRANSLATION = {
        'OFFICER_NAME': 'نام مدیر',
        'OFFICER_FAMILY': 'نام خانوادگی مدیر',
        'OFFICER_SOCIAL_NUMBER': 'کد ملی مدیر',
        'PERSONNEL_ID': 'کد پرسنلی مدیر',
        'BRANCH_CODE': 'کد شعبه',
        'BRANCH_NAME': 'نام شعبه',
        'NAME': 'نام مشتری',
        'FAMILY': 'نام خانوادگی مشتری',
        'SSN': 'کد ملی مشتری',
        'CELL_PHONE_NO': 'شماره تماس مشتری',
        'STATUS': 'وضعیت مشتری',
        'TYPE': 'نوع مشتری',
    }

    OFFICER_SEARCH_TRANSLATION = {
        'NAME': 'نام مدیر',
        'FAMILY': 'نام خانوادگی مدیر',
        'PERSONNEL_ID': 'کد پرسنلی مدیر',
        'SSN': 'کد ملی مدیر',
        'CELL_PHONE_NO': 'شماره تماس مدیر',
        'BRANCH_CODE': 'کد شعبه',
        'BRANCH_NAME': 'نام شعبه',
        'SUPERVISOR_SOCIAL_NUMBER': 'کد ملی ناظر',
        'SUPERVISOR_NAME': 'نام ناظر',
        'SUPERVISOR_FAMILY': 'نام خانوادگی ناظر',
        'SUPERVISOR_PERSONNEL_ID': 'کد پرسنلی ناظر',
        'TYPE': 'نوع مدیر',
        'STATUS': 'وضعیت مدیر'
    }
    SUPERVISOR_SEARCH_TRANSLATION = {
        'NAME': 'نام',
        'FAMILY': 'نام خانوادگی',
        'PERSONNEL_ID': 'شماره پرسنلی',
        'SSN': 'کد ملی',
        'CELL_PHONE_NO': 'شماره تماس',
        'BRANCH_CODE': 'کد شعبه',
        'BRANCH_NAME': 'نام شعبه',
        'STATUS': 'وضعیت',
    }
