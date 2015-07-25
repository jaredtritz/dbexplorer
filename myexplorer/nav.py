from django.core.urlresolvers import reverse

def tab_nav(user, selected):
    menu = [
            ['Database Map', 
                '',  
                    reverse('myexplorer:manage_datamap'),
                        'manage_datamap'
            ],
            ['Samples', 
                '',  
                    reverse('myexplorer:manage_samples'),
                        'manage_samples'
            ],
            ['Analysis', 
                '',  
                    reverse('myexplorer:manage_analysis'),
                        'manage_analysis'
            ],
            ['Reports', 
                '',  
                    reverse('myexplorer:manage_reports'),
                        'manage_reports'
            ],
        ]

    nav = []
    for nn in menu:
        # style the selected option
        if nn[3] == selected:
            nn[1] = 'active'
        nav.append(nn)
    return nav

def side_database_manager(user, selected):
    menu = [
            #'text'         
            #   'styling_class(es)',    
            #       'links_to'
            #           'selected'
            ['Retrieve Schema', 
                '',  
                    reverse('myexplorer:get_table_schema'),
                        'get_table_schema'
            ],
            ['All Schema', 
                '',  
                    reverse('myexplorer:table_schema'),
                        'table_schema'
            ],
            ['No ADSNAP Schema', 
                '',  
                    reverse('myexplorer:table_schema_no_adsnap'),
                        'table_schema_no_adsnap'
            ],
            ['Transfer Schema', 
                '',  
                    reverse('myexplorer:table_schema_transfer'),
                        'table_schema_transfer'
            ],
        ]
    nav = []
    for nn in menu:
        # style the selected option
        if nn[3] == selected:
            nn[1] = 'active'
        nav.append(nn)
    return nav

def side_analysis_manager(user, selected):
    menu = [
            ['Extract Properties', 
                '',  
                    reverse('myexplorer:canned_properties'),
                        'canned_properties'
            ],
            ['Make Comparisons', 
                '',  
                    reverse('myexplorer:canned_comparisons'),
                        'canned_comparisons'
            ],
        ]

    nav = []
    for nn in menu:
        # style the selected option
        if nn[3] == selected:
            nn[1] = 'active'
        nav.append(nn)
    return nav

def side_sample_manager(user, selected):
    menu = [
            #'text'         
            #   'styling_class(es)',    
            #       'links_to'
            #           'selected'
            ['Upload Sample', 
                '',  
                    reverse('myexplorer:upload_sample'),
                        'upload_sample'
            ],
            ['Filter Sample', 
                '',
                    reverse('myexplorer:filter_sample'),
                        'filter_sample'
            ],
            ['Sub Sample', 
                '',  
                    reverse('myexplorer:sub_sample'),
                        'sub_sample'
            ],
            #['Merge Samples', 
            #    '',  
            #        reverse('myexplorer:merge_sample'),
            #            'merge_sample'
            #],
            ['--------------------------', 
                'nav-header',  
                    '',
                        ''
            ],
            ['Retrieve Sample Data', 
                '',  
                    reverse('myexplorer:review_samples'),
                        'review_samples'
            ],
            ['Browse Sample', 
                '',  
                    reverse('myexplorer:browse_sample'),
                        'browse_sample'
            ]
        ]

    nav = []
    for nn in menu:
        # style the selected option
        if nn[3] == selected:
            nn[1] = 'active'
        nav.append(nn)
    return nav


def side_report_manager(user, selected):
    menu = [
            #'text'         
            #   'styling_class(es)',    
            #       'links_to'
            #           'selected'
            ['Database', 
                '',
                    reverse('myexplorer:database_reports'),
                        'database_reports'
            ],
            ['Samples', 
                '',
                    reverse('myexplorer:sample_reports'),
                        'sample_reports'
            ],
            ['Analysis', 
                '',
                    reverse('myexplorer:analysis_reports'),
                        'analysis_reports'
            ],
        ]

    nav = []
    for nn in menu:
        # style the selected option
        if nn[3] == selected:
            nn[1] = 'active'
        nav.append(nn)
    return nav

