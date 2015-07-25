from django.conf.urls import patterns, include, url
from django.conf import settings
from .views import *
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'transfer.views.home', name='home'),
    # url(r'^transfer/', include('transfer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # tab 1
    url(r'^manage_datamap/$', login_required(manage_datamap_view), name='manage_datamap'),
    url(r'^get_table_schema/$', login_required(get_table_schema_view), name='get_table_schema'),
    url(r'^table_schema/$', login_required(table_schema_view), name='table_schema'),
    url(r'^table_schema_no_adsnap/$', login_required(table_schema_no_adsnap_view), name='table_schema_no_adsnap'),
    url(r'^table_schema_transfer/$', login_required(table_schema_transfer_view), name='table_schema_transfer'),
        # ajax
        url(r'^table_column_hist/$', login_required(table_column_hist_view), name='table_column_hist'),
        url(r'^new_filter/$', login_required(new_filter_view), name='new_filter'),
        url(r'^add_to_filter/$', login_required(add_to_filter_view), name='add_to_filter'),
    # tab 2
    url(r'^manage_samples/$', login_required(manage_samples_view), name='manage_samples'),
    url(r'^upload_sample/$', login_required(upload_sample_view), name='upload_sample'),
    url(r'^filter_sample/$', login_required(filter_sample_view), name='filter_sample'),
    url(r'^sub_sample/$', login_required(sub_sample_view), name='sub_sample'),
    url(r'^merge_sample/$', login_required(merge_sample_view), name='merge_sample'),
    url(r'^review_samples/$', login_required(review_samples_view), name='review_samples'),
    url(r'^browse_sample/$', login_required(browse_sample_view), name='browse_sample'),
        url(r'^retrieve_sample_ajax/$', login_required(retrieve_sample_ajax_view), name='retrieve_sample_ajax'),
        url(r'^retrieve_osample_ajax/$', login_required(retrieve_osample_ajax_view), name='retrieve_osample_ajax'),
        url(r'^retrieve_oresult_ajax/$', login_required(retrieve_oresult_ajax_view), name='retrieve_oresult_ajax'),
        url(r'^sample_hist/$', login_required(sample_hist_view), name='sample_hist'),
    # tab 3
    url(r'^manage_analysis/$', login_required(manage_analysis_view), name='manage_analysis'),
    url(r'^canned_properties/$', login_required(canned_properties_view), name='canned_properties'),
    url(r'^canned_comparisons/$', login_required(canned_comparisons_view), name='canned_comparisons'),
        url(r'^calculate_properties_ajax/$', login_required(calculate_properties_ajax_view), name='calculate_properties_ajax'),
        url(r'^make_comparisons_ajax/$', login_required(make_comparisons_ajax_view), name='make_comparisons_ajax'),
    # tab 4
    url(r'^manage_reports/$', login_required(manage_reports_view), name='manage_reports'),
    url(r'^report/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.HTML_ROOT}, name='html_reports'),
    url(r'^database_reports/$', login_required(database_reports_view), name='database_reports'),
    url(r'^sample_reports/$', login_required(sample_reports_view), name='sample_reports'),
    url(r'^analysis_reports/$', login_required(analysis_reports_view), name='analysis_reports'),
    # default
    url(r'^download_mysql_db/', login_required(Download_Mysql_View), name='download_mysql'), # hack for now
    url(r'^', login_required(default_view), name='default'),
)
