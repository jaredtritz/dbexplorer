from django.shortcuts import render_to_response, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from datetime import datetime
from .models import *
from .nav import *
import pandas
import json
import random
import thread
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory, modelform_factory
from .forms import *

# Create your views here.

def default_view(request):
    return render(request, 'myexplorer/about.html', {})

@staff_member_required
def manage_datamap_view(request):
    return redirect(reverse('myexplorer:table_schema_transfer'))

@staff_member_required
def manage_samples_view(request):
    return redirect(reverse('myexplorer:upload_sample'))

@staff_member_required
def manage_analysis_view(request):
    return redirect(reverse('myexplorer:canned_properties'))

@staff_member_required
def manage_reports_view(request):
    return redirect(reverse('myexplorer:database_reports'))

@staff_member_required
def get_table_schema_view(request):
    new_tables = []
    updated_tables = []
    if request.method == 'POST':
        form = Retrieve_Schema_Form(
            data=request.POST, 
        )
        if form.is_valid():
            trigger = form.cleaned_data['trigger']
            # go get the table schema
            new_tables = Table.get_tables()
            updated_tables = Table.get_column_data()
    form = Retrieve_Schema_Form()
    return render(request, 'myexplorer/get_table_schema.html', {
        'tab_nav': tab_nav(request.user, 'manage_datamap'),
        'side_nav': side_database_manager(request.user, 'get_table_schema'),
        'form' : form,
        'new_tables': new_tables,
        'updated_tables': new_tables,
    })

@staff_member_required
def table_schema_view(request):
    tables = Table.objects.all()
    tdata = []
    for tt in tables:
        tdata.append(tt.to_html())
    hist_form = Table_Column_Data_Histogram_Form()
    new_filter_form = New_Filter_Form()
    add_to_filter_form = Add_To_Filter_Form()
    return render(request, 'myexplorer/explore_tables.html', {
        'tab_nav': tab_nav(request.user, 'manage_datamap'),
        'side_nav': side_database_manager(request.user, 'table_schema'),
        'tables': tdata,
        'hist_form': hist_form,
        'new_filter_form': new_filter_form,
        'add_to_filter_form': add_to_filter_form,
    })

@staff_member_required
def table_schema_no_adsnap_view(request):
    tables = Table.objects.all()
    tables = [tt for tt in tables if tt.name.find('ADSNAP') < 0]
    tdata = []
    for tt in tables:
        tdata.append(tt.to_html())
    hist_form = Table_Column_Data_Histogram_Form()
    new_filter_form = New_Filter_Form()
    add_to_filter_form = Add_To_Filter_Form()
    return render(request, 'myexplorer/explore_tables.html', {
        'tab_nav': tab_nav(request.user, 'manage_datamap'),
        'side_nav': side_database_manager(request.user, 'table_schema_no_adsnap'),
        'tables': tdata,
        'hist_form': hist_form,
        'new_filter_form': new_filter_form,
        'add_to_filter_form': add_to_filter_form,
    })

@staff_member_required
def table_schema_transfer_view(request):
    tables = Table.objects.all()
    trans_tables = [
    'TRNS_OTHR_MODEL',
    'TRNS_OTHR_TERM',
    'TRNS_OTHR_DTL',

    'TRNS_CRSE_TERM',
    'TRNS_CRSE_SCH',
    'TRNS_CRSE_DTL',

    'TRNS_TEST_MODEL',
    'TRNS_TEST_TERM',
    'TRNS_TEST_DTL',

    'EXT_COURSE',
    'EXT_TRANSCRIPT',
    'EXT_DEGREE',
    'EXT_ACAD_DATA',
    'EXT_ACAD_SUBJ',
    'EXT_ACAD_SUM',
    'EXT_ORG_TBL',

    'ACAD_PLAN',
    'ACAD_PROG',
    'ACAD_DEGR',
    'ACAD_SUBPLAN',
    'ACAD_DEGR_PLAN',

    'STDNT_CAR_TERM',
    'STDNT_CAREER',
    'STDNT_ENRL',

    'ADM_APPL_DATA',
    'ADM_APPL_PROG',

    'PERSONAL_DATA',
    'ETHNICITY_DTL',
    'GEOLOC',
    ''
    ]
    tables = [tt for tt in tables if tt.name in trans_tables]
    tdata = []
    for tt in tables:
        tdata.append(tt.to_html())
    hist_form = Table_Column_Data_Histogram_Form()
    new_filter_form = New_Filter_Form()
    add_to_filter_form = Add_To_Filter_Form()
    return render(request, 'myexplorer/explore_tables.html', {
        'tab_nav': tab_nav(request.user, 'manage_datamap'),
        'side_nav': side_database_manager(request.user, 'table_schema_transfer'),
        'tables': tdata,
        'hist_form': hist_form,
        'new_filter_form': new_filter_form,
        'add_to_filter_form': add_to_filter_form,
    })

@staff_member_required
def sample_hist_view(request): 
    # create the historgram
    if request.method == 'POST':
        form = Sample_Column_Data_Histogram_Form(data=request.POST)
        if form.is_valid():
            sample = Sample.objects.get(id=form.cleaned_data['hist_sample'])
            ref = form.cleaned_data['hist_table_ref']
            table = form.cleaned_data['hist_table']
            column = form.cleaned_data['hist_column']
            kind = form.cleaned_data['hist_kind']
            # do analysis
            if kind == 'col_dist': 
                lpairs = sample.table_column_distribution(ref, table, column)
                plot_xlab = 'Distribution in '+ref+'.'+table+'.'+column
                plot_ylab = 'Counts: ' + str(sum(zip(*lpairs)[1]))
                plot_title = 'Histogram'
            if kind == 'num_entries': 
                lpairs = sample.table_column_num_entries(ref, table, column)
                plot_xlab = 'Entries per student in '+ref+'.'+table
                plot_ylab = 'Counts: ' + str(sum(zip(*lpairs)[1]))
                plot_title = 'Histogram'
            resp = render(request, 'myexplorer/table_column_hist.html', {
                'plot_xlab': plot_xlab,
                'plot_ylab': plot_ylab,
                'plot_title': plot_title,
                'plot_pairs': lpairs
            })
            # create report object
            report = Report(user=request.user, name=plot_xlab, sample=sample, created=datetime.now(), rtype='sample')  
            report.save()
            # save the html to file
            ofile = settings.HTML_ROOT + str(report.id) + '_report.html'
            htmlstr = resp.content
            Html_file= open(ofile,"w")
            Html_file.write(htmlstr)
            Html_file.close
            # return the html
            return resp
    return HttpResponse("Unable to create histogram")

@staff_member_required
def table_column_hist_view(request): 
    success = True
    if request.method == 'POST':
        form = Table_Column_Data_Histogram_Form(data=request.POST)
        if form.is_valid():
            ref = form.cleaned_data['hist_table_ref']
            table = form.cleaned_data['hist_table']
            column = form.cleaned_data['hist_column']
            hist_type = form.cleaned_data['hist_type']
            if hist_type == 'cat':
                success, msg, lpairs = Table.cat_hist(ref, table, column)
                if success:
                    plot_xlab = ref+'.'+table+'.'+ column
                    plot_ylab = 'Counts: ' + str(sum(zip(*lpairs)[1]))
                    plot_title = 'Categorical Histogram'
            elif hist_type == 'num':
                min_num = form.cleaned_data['hist_min_num']
                max_num = form.cleaned_data['hist_max_num']
                roundto = form.cleaned_data['hist_numroundto']
                success, msg, lpairs = Table.num_hist(ref, table, column, roundto, min_num, max_num)
                if success:
                    plot_xlab = ref+'.'+table+'.'+ column
                    plot_ylab = 'Counts: ' + str(sum(zip(*lpairs)[1]))
                    plot_title = 'Numeric Histogram'
            elif hist_type == 'date':
                min_date = form.cleaned_data['hist_min_date']
                max_date = form.cleaned_data['hist_max_date']
                roundto = form.cleaned_data['hist_dateroundto']
                success, msg, lpairs = Table.date_hist(ref, table, column, min_date, max_date, roundto)
                if success:
                    plot_xlab = ref+'.'+table+'.'+ column
                    plot_ylab = 'Counts: ' + str(sum(zip(*lpairs)[1]))
                    plot_title = 'Numeric Histogram'
    if not success:
        return HttpResponse(msg)
    # create the historgram
    resp = render(request, 'myexplorer/table_column_hist.html', {
        'plot_xlab': plot_xlab,
        'plot_ylab': plot_ylab,
        'plot_title': plot_title,
        'plot_pairs': lpairs
    })
    # create report object
    report = Report(user=request.user, name=plot_xlab, created=datetime.now(), rtype='database')  
    report.save()
    # save the html to file
    ofile = settings.HTML_ROOT + str(report.id) + '_report.html'
    htmlstr = resp.content
    Html_file= open(ofile,"w")
    Html_file.write(htmlstr)
    Html_file.close
    # return the html
    return resp

@staff_member_required
def new_filter_view(request): # ajax service
    # add the filter
    if request.method == 'POST':
        form = New_Filter_Form(data=request.POST)
        if form.is_valid():
            filter_name = form.cleaned_data['new_filter_name']
            filter_join = form.cleaned_data['new_filter_join']
            sfilter = SampleFilter(user=request.user, name=filter_name, ref_table_column=filter_join)
            sfilter.save()
    else:
        form = New_Filter_Form()
    return HttpResponse("sucess")

@staff_member_required
def add_to_filter_view(request): # ajax service
    # add the filter part
    ret = "Failed to add filter part!"
    if request.method == 'POST':
        form = Add_To_Filter_Form(data=request.POST)
        if form.is_valid():
            sfilter = form.cleaned_data['addto_filter_name']
            fref = form.cleaned_data['addto_filter_table_ref']
            ftable = form.cleaned_data['addto_filter_table']
            fcol = form.cleaned_data['addto_filter_column']
            ftype = form.cleaned_data['addto_filter_type']
            fpart = SampleFilterPart(sample_filter=sfilter, ref=fref, table=ftable, filter_col=fcol, ftype=ftype)
            if ftype == 'cat':
                ret = fpart.Retrieve_Cats()
            else:
                ret = "Success adding filter for " + fcol
            fpart.save()
    return HttpResponse(ret)

@staff_member_required
def filter_sample_view(request):
    NumFormSet = modelformset_factory(
        SampleFilterPart,
        can_delete=True,
        form=Sample_Filter_Num_Form,
        extra = 0,
    )
    DateFormSet = modelformset_factory(
        SampleFilterPart,
        can_delete=True,
        form=Sample_Filter_Date_Form,
        extra = 0,
    )
    CatFormSet = modelformset_factory(
        SampleFilterPart, 
        can_delete=True,
        form=Sample_Filter_Cat_Form,
        extra=0,
    )
    num_students = 0
    sfilter = SampleFilter() # start with empty filter
    if request.method == 'POST':
        # maybe populate filter
        filterform = Filter_Select_Form(
            data=request.POST, 
        )
        if filterform.is_valid():
            sfilter = filterform.cleaned_data['sfilter']
        # numeric parts
        numformset = NumFormSet(
            prefix='num',
            data=request.POST, 
        )
        if numformset.total_form_count() == 0 or (numformset[0].instance.sample_filter != sfilter):
            numformset = NumFormSet(
                prefix='num',
                queryset=SampleFilterPart.objects.filter(sample_filter=sfilter, ftype='num')
            )
        elif numformset.is_valid() and len(numformset.deleted_forms) > 0:
            numformset.save()
            numformset = NumFormSet(
                prefix='num',
                queryset=SampleFilterPart.objects.filter(sample_filter=sfilter, ftype='num')
            )
        # catagoric parts
        catformset = CatFormSet(
            prefix='cat',
            data=request.POST, 
        )
        if catformset.total_form_count() == 0 or (catformset[0].instance.sample_filter != sfilter):
            catformset = CatFormSet(
                prefix='cat',
                queryset=SampleFilterPart.objects.filter(sample_filter=sfilter, ftype='cat')
            )
        elif catformset.is_valid() and len(catformset.deleted_forms) > 0:
            catformset.save()
            catformset = CatFormSet(
                prefix='cat',
                queryset=SampleFilterPart.objects.filter(sample_filter=sfilter, ftype='cat')
            )
        # date parts
        dateformset = DateFormSet(
            prefix='date',
            data=request.POST, 
        )
        if dateformset.total_form_count() == 0 or (dateformset[0].instance.sample_filter != sfilter):
            dateformset = DateFormSet(
                prefix='date',
                queryset=SampleFilterPart.objects.filter(sample_filter=sfilter, ftype='date')
            )
        elif dateformset.is_valid() and len(dateformset.deleted_forms) > 0:
            dateformset.save()
            dateformset = DateFormSet(
                prefix='date',
                queryset=SampleFilterPart.objects.filter(sample_filter=sfilter, ftype='date')
            )
        # new filter 
        newsampleform = New_Sample_Form(data=request.POST)
        # proces the forms to create query
        froms = []
        if sfilter.ref_table_column != None:
            froms = ['.'.join(sfilter.ref_table_column.split('.')[0:2])]
            catwhere = []
            numwheremin = []
            numwheremax = []
            datewheremin = []
            datewheremax = []
            for catform in catformset:
                if catform.is_valid():
                    mod = catform.instance
                    if len(catform.cleaned_data['categories']) > 0:
                        froms.append('.'.join([mod.ref, mod.table]))
                        catwhere.append(['.'.join([mod.ref, mod.table, mod.filter_col]), catform.cleaned_data['categories']])
            for numform in numformset:
                if numform.is_valid():
                    mod = numform.instance
                    if isinstance(numform.cleaned_data['min_num'], float):
                        froms.append('.'.join([mod.ref, mod.table]))
                        numwheremin.append(['.'.join([mod.ref, mod.table, mod.filter_col]), numform.cleaned_data['min_num']])
                    if isinstance(numform.cleaned_data['max_num'], float):
                        froms.append('.'.join([mod.ref, mod.table]))
                        numwheremax.append(['.'.join([mod.ref, mod.table, mod.filter_col]), numform.cleaned_data['max_num']])
            for dateform in dateformset:
                if dateform.is_valid():
                    mod = dateform.instance
                    if isinstance(dateform.cleaned_data['min_date'], float): 
                        froms.append('.'.join([mod.ref, mod.table]))
                        datewheremin.append(['.'.join([mod.ref, mod.table, mod.filter_col]), dateform.cleaned_data['min_date']])
                    if isinstance(dateform.cleaned_data['max_date'], float): 
                        froms.append('.'.join([mod.ref, mod.table]))
                        datewheremax.append(['.'.join([mod.ref, mod.table, mod.filter_col]), dateform.cleaned_data['max_date']])
            froms = set(froms)
            try:
                con = cx_Oracle.connect('jtritz/jt47519@pa02.world')
                query = """\n\tselect"""
                newsampleform.full_clean()
                # either count ids or pull the actual ids
                if newsampleform.cleaned_data['new_sample_trigger']:
                    query += """\n\tdistinct """ + sfilter.ref_table_column
                else:
                    query += """\n\tcount(distinct """ + sfilter.ref_table_column + """)"""
                query += """\n\tfrom"""
                query += """\n\t""" + ', \n\t'.join(froms) 
                query += """\n\twhere 1=1"""
                for ff in froms:
                    query += """\n\tand """ + sfilter.ref_table_column + """ = """ + ff + """.""" + sfilter.ref_table_column.split('.')[-1] 
                for ww in catwhere:
                    query += ("""\n\tand """ + ww[0] + """ in ('""" + "', '".join(ww[1]) + """')""")
                for ww in numwheremin:
                    query += ("""\n\tand """ + ww[0] + """ > """ + str(ww[1]))
                for ww in numwheremax:
                    query += ("""\n\tand """ + ww[0] + """ < """ + str(ww[1]))
                for ww in datewheremin:
                    query += """\n\tand ((cast(""" + ww[0] + """ as date) - date '1970-01-01')*24*60*60) > """ + str(ww[1])
                for ww in datewheremax:
                    query += """\n\tand ((cast(""" + ww[0] + """ as date) - date '1970-01-01')*24*60*60) < """ + str(ww[1])
                # what to do with the query
                if newsampleform.cleaned_data['test_sample_trigger']:
                    cur = con.cursor()
                    cur.execute(query)
                    new = cur.fetchall()
                    num_students = new[0][0]
                elif newsampleform.cleaned_data['new_sample_trigger']:
                    cur = con.cursor()
                    cur.execute(query)
                    new = cur.fetchall()
                    new_ids = [ii[0] for ii in new]
                    sname = newsampleform.cleaned_data['new_sample_name']
                    key_col = sfilter.ref_table_column.split('.')[2]
                    Sample.add(user=request.user, pks=new_ids, sample_name=sname, key_col=key_col, stype='Filter', detail=query)
                con.close()
            except cx_Oracle.DatabaseError, exc:
                success = False
                error, = exc.args
                body = ""
                body += "Failed to execute this filter..."
                body += "<br>Oracle-Error-Code: " + str(error.code)
                body += "<br>Oracle-Error-Message: " + str(error.message)
                return HttpResponse(body)

    else:
        filterform = Filter_Select_Form()
        dateformset = DateFormSet(
            prefix='date',
            queryset=SampleFilterPart.objects.filter(sample_filter=sfilter, ftype='date')
        )
        numformset = NumFormSet(
            prefix='num',
            queryset=SampleFilterPart.objects.filter(sample_filter=sfilter, ftype='num')
        )
        catformset = CatFormSet(
            prefix='cat',
            queryset=SampleFilterPart.objects.filter(sample_filter=sfilter, ftype='cat')
        )
    newsampleform = New_Sample_Form()
    return render(request, 'myexplorer/filter_sample.html', {
        'tab_nav': tab_nav(request.user, 'manage_samples'),
        'side_nav': side_sample_manager(request.user, 'filter_sample'),
        'filterform': filterform,
        'sfilter': sfilter,
        'dateformset': dateformset,
        'numformset': numformset,
        'catformset': catformset,
        'newsampleform': newsampleform,
        'num_students': num_students
    })

@staff_member_required
def upload_sample_view(request):
    ids = []
    if request.method == 'POST':
        form = Fixed_Ids_Upload_Form(request.POST, request.FILES)
        if form.is_valid():
            sample_name = form.cleaned_data['sample_name']
            sample_key_column = form.cleaned_data['sample_key_column']
            ufile = form.cleaned_data['csv_file']
            ids = ufile.read().splitlines()
            # create the sample
            Sample.add(user=request.user, pks=ids, sample_name=sample_name, key_col=sample_key_column, stype='Upload')
            form = Fixed_Ids_Upload_Form() # when it's done clear
    else:
        form = Fixed_Ids_Upload_Form()
    return render(request, 'myexplorer/upload_sample.html', {
        'tab_nav': tab_nav(request.user, 'manage_samples'),
        'side_nav': side_sample_manager(request.user, 'upload_sample'),
        'form': form,
        'fixed': ids,
    })

@staff_member_required
def sub_sample_view(request):
    olds = []
    news = []
    if request.method == 'POST':
        form = Sub_Sample_Form(
            data=request.POST, 
        )
        if form.is_valid():
            sample=form.cleaned_data['sample']
            sub_name = form.cleaned_data['sub_name']
            sub_size = form.cleaned_data['sub_size']
            # create the sub-sample
            olds = OSample.objects.filter(sample=sample)
            new_ids = [ss.oid for ss in random.sample(olds, sub_size)]
            Sample.add(user=request.user, pks=new_ids, sample_name=sub_name, key_col=sample.key_column, stype='Sub', detail=('from: ' + sample.name))
            olds = []
            form = Sub_Sample_Form()
    else:
        form = Sub_Sample_Form()
    if hasattr(form, 'cleaned_data'):
        if 'sample' in form.cleaned_data.keys():
            sample = form.cleaned_data['sample']
            olds = OSample.objects.filter(sample=sample)
    return render(request, 'myexplorer/sub_sample.html', {
        'tab_nav': tab_nav(request.user, 'manage_samples'),
        'side_nav': side_sample_manager(request.user, 'sub_sample'),
        'form': form,
        'olds': olds,
        'news': news,
    })

@staff_member_required
def merge_sample_view(request):
    return render(request, 'myexplorer/merge_samples.html', {
        'tab_nav': tab_nav(request.user, 'manage_samples'),
        'side_nav': side_sample_manager(request.user, 'merge_sample'),
    })

@staff_member_required
def review_samples_view(request):
    samples = Sample.objects.all()
    return render(request, 'myexplorer/review_samples.html', {
        'tab_nav': tab_nav(request.user, 'manage_samples'),
        'side_nav': side_sample_manager(request.user, 'review_samples'),
        'samples': samples,
    })

@staff_member_required
def retrieve_sample_ajax_view(request):
    if request.method == 'GET':
        sample_id = request.GET['sample']
        #from .tasks import add, test
        #add.apply_async((3,2), serializer='json')
        #test.apply_async((request.user,), serializer='json')
        from .tasks import sample_retriever
        link = HttpRequest.build_absolute_uri(request, reverse('myexplorer:browse_sample'))
        sample_retriever.apply_async((request.user.username, sample_id, link,), serializer='json')
        #Sample.retrieve(request.user.username, sample_id)
        #thread.start_new_thread(Sample.retrieve, (sample_id,))
    return HttpResponse('success')

@staff_member_required
def browse_sample_view(request):
    if request.method == 'POST':
        choose_sample_form = Browse_Sample_Form(
            data=request.POST, 
        )
    else:
        choose_sample_form = Browse_Sample_Form(
            #choices = OSample.choice_tuple()
        )
    sample_column_hist_form = Sample_Column_Data_Histogram_Form()
    return render(request, 'myexplorer/browse_sample.html', {
        'tab_nav': tab_nav(request.user, 'manage_samples'),
        'side_nav': side_sample_manager(request.user, 'browse_sample'),
        'sample_column_hist_form': sample_column_hist_form,
        'choose_sample_form': choose_sample_form,
    })

@staff_member_required
def retrieve_osample_ajax_view(request):
    sample_obj = None
    results = []
    if request.method == 'GET':
        sample_id = int(request.GET['sample_id'])
        mod_osample = int(request.GET['mod_osample'])
        sample = Sample.objects.get(id=sample_id)
        osample_pks = sample.osample_set.values_list('id')
        len_objs = len(osample_pks)
        if len_objs > 0:
            ind = mod_osample % len_objs
            sample_obj = OSample.objects.get(id=osample_pks[ind][0])
            #results = sample_obj.result_set.exclude(data=None)
            results = Result.objects.filter(osample=sample_obj)
        rdata = []
        for rr in results:
            rdata.append(rr.to_html())
    return render(request, 'myexplorer/osample_results.html', {
        'sample_obj': sample_obj,
        'rdata': rdata,
    })

@staff_member_required
def retrieve_oresult_ajax_view(request):
    sample_obj = None
    results = []
    mod_osample = 0
    if request.method == 'GET':
        sample_id = int(request.GET['sample_id'])
        mod_osample = int(request.GET['mod_osample'])
        mod_direction = request.GET['mod_direction']
        ref = request.GET['ref']
        table = request.GET['table']
        sample = Sample.objects.get(id=sample_id)
        osample_pks = sample.osample_set.values_list('id')
        len_objs = len(osample_pks)
        if len_objs > 0:
            start_ind = mod_osample % len_objs
            wrapped = False
            while len(results) == 0 and not wrapped:
                ind = mod_osample % len_objs
                sample_obj = OSample.objects.get(id=osample_pks[ind][0])
                results = sample_obj.result_set.filter(ref=ref, table=table).exclude(data=None)
                rdata = []
                for rr in results:
                    rdata.append(rr.to_html())
                # increment and mod index
                if mod_direction == '+':
                    mod_osample += 1
                else:
                    mod_osample -= 1
                ind = mod_osample % len_objs
                if len(rdata) > 0 or ind == start_ind:
                    wrapped = True
    # fix osample skips 
    if mod_direction == '+':
        mod_osample -= 1
    else:
        mod_osample += 1
    res = render(request, 'myexplorer/osample_results.html', {
        'sample_obj': sample_obj,
        'rdata': rdata,
    })
    json_data = json.dumps({'html':res.content, 'mod_osample':mod_osample})
    return HttpResponse(json_data, mimetype="application/json")

@staff_member_required
def canned_properties_view(request):
    sproperties = []
    sample = None
    if request.method == 'POST':
        properties_sample_form = Properties_Sample_Form(
            data=request.POST, 
        )
        if properties_sample_form.is_valid():
            sample = properties_sample_form.cleaned_data['sample']
            sample.sync_properties()
            sproperties = SProperty.objects.filter(sample=sample).order_by('label')
    else:
        properties_sample_form = Properties_Sample_Form(
            #choices = OSample.choice_tuple()
        )
    # send to page
    return render(request, 'myexplorer/canned_properties.html', {
        'tab_nav': tab_nav(request.user, 'manage_analysis'),
        'side_nav': side_analysis_manager(request.user, 'canned_properties'),
        'properties_sample_form': properties_sample_form,
        'sproperties': sproperties,
        'sample': sample,
    })

@staff_member_required
def calculate_properties_ajax_view(request):
    if request.method == 'GET':
        sproperties = json.loads(request.GET['sproperties'])
        email = request.GET['email']
        from .tasks import property_calculator
        property_calculator.apply_async((sproperties, request.user.username, email,), serializer='json')
        #sample.calculate_properties(sproperties, request.user.username, email)
    return HttpResponse('success')

@staff_member_required
def canned_comparisons_view(request):
    cprops = []
    sampleA = None
    sampleB = None
    if request.method == 'POST':
        comparisons_sample_form = Comparisons_Sample_Form(
            data=request.POST, 
        )
        if comparisons_sample_form.is_valid():
            sampleA = comparisons_sample_form.cleaned_data['sampleA']
            sampleB = comparisons_sample_form.cleaned_data['sampleB']
            # to help ensure 'A comp B' and 'B comp A' are same thing A will always be smaller
            if sampleB.id < sampleA.id:
                tmp = sampleA
                sampleA = sampleB
                sampleB = tmp
            spropertiesA = SProperty.objects.filter(sample=sampleA, status='Loaded')
            spropertiesB = SProperty.objects.filter(sample=sampleB, status='Loaded')
            # find property intersection
            sprops_both = []
            for pa in spropertiesA:
                for pb in spropertiesB:
                    if pa.method == pb.method and pa.id != pb.id:
                        sprops_both.append([pa, pb])
            Comparison.sync_comparisons(sprops_both)
            if len(sprops_both) > 0:
                comps = Comparison.objects.filter(spropertyA__in=zip(*sprops_both)[0], spropertyB__in=zip(*sprops_both)[1])
                cdict = dict()
                for cc in comps:
                    mkey = cc.spropertyA.label
                    mtype = cc.spropertyA.vtype
                    if not mkey in cdict:
                        cdict[mkey] = [mtype,[]] 
                    cdict[mkey][1].append(cc)
                cms = []
                for cp in cdict:
                    cprops.append([cp, cdict[cp][0], cdict[cp][1]])
                cprops = sorted(cprops, key=lambda x: x[0])
    else:
        comparisons_sample_form = Comparisons_Sample_Form(
            #choices = OSample.choice_tuple()
        )
    # send to page
    return render(request, 'myexplorer/canned_comparisons.html', {
        'tab_nav': tab_nav(request.user, 'manage_analysis'),
        'side_nav': side_analysis_manager(request.user, 'canned_comparisons'),
        'comparisons_sample_form': comparisons_sample_form,
        'sampleA': sampleA,
        'sampleB': sampleB,
        'cprops': cprops,
    })

@staff_member_required
def make_comparisons_ajax_view(request):
    if request.method == 'GET':
        comp_ids = json.loads(request.GET['comp_ids'])
        from .tasks import comparison_calculator
        comparison_calculator.apply_async((request.user.username, comp_ids,), serializer='json')
        #Comparison.calculate_comparisons(request.user.username, comp_ids)
    return HttpResponse('success')

@staff_member_required
def database_reports_view(request):
    reports = Report.objects.filter(rtype='database').order_by('-id')
    return render(request, 'myexplorer/database_reports.html', {
        'tab_nav': tab_nav(request.user, 'manage_reports'),
        'side_nav': side_report_manager(request.user, 'database_reports'),
        'html_root': settings.HTML_ROOT,
        'reports': reports,
    })

@staff_member_required
def sample_reports_view(request):
    reports = Report.objects.filter(rtype='sample').order_by('-id')
    return render(request, 'myexplorer/sample_reports.html', {
        'tab_nav': tab_nav(request.user, 'manage_reports'),
        'side_nav': side_report_manager(request.user, 'sample_reports'),
        'html_root': settings.HTML_ROOT,
        'reports': reports,
    })

@staff_member_required
def analysis_reports_view(request):
    reports = Report.objects.filter(rtype='analysis').order_by('comparison__spropertyA__label')
    return render(request, 'myexplorer/analysis_reports.html', {
        'tab_nav': tab_nav(request.user, 'manage_reports'),
        'side_nav': side_report_manager(request.user, 'analysis_reports'),
        'html_root': settings.HTML_ROOT,
        'reports': reports,
    })

@staff_member_required
def Download_Mysql_View(request):
    import os, time
    # if not admin don't do it
    staffmember = request.user.is_staff
    if not staffmember:
        return redirect('/')
    # send the results
    try:
        now = time.strftime('%Y-%m-%d-%H-%M-%S')         
        file_name = settings.DB_NAME + "_" + now + ".sql"
        file_path = settings.DIR_DOWNLOAD_DATA + "mysql/" + file_name
        
        os.system("mysqldump -u "+settings.DB_USER+" -p"+settings.DB_PASS+" " + settings.DB_NAME + " > " + file_path)

        fsock = open(file_path,"rb")
        response = HttpResponse(fsock, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=' + file_name            
    except IOError:
        response = HttpResponseNotFound("error creating backup database file")
    return response


