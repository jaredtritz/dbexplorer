from django.db import models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from functools import wraps
import cx_Oracle
import pandas
import json
from datetime import datetime
from pytz import timezone
import numpy as np

# Create your models here.

class Table(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    ref = models.CharField(max_length=50, null=True, blank=True)
    headers = models.TextField(null=True, blank=True) # json 
    data = models.TextField(null=True, blank=True) # json 

    @classmethod
    def get_tables(self):
        con = cx_Oracle.connect('username/password@server')
        query = "select * from all_tables"
        cur = con.cursor()
        cur.execute(query)
        new = []
        for res in cur:
            tt = Table.objects.get_or_create(ref=res[0], name=res[1]) 
            if tt[1]:
                new.append(tt[0])
                tt[0].save()
            """
            table = Table.objects.filter(ref=res[0], name=res[1]) 
            if len(table) < 1:
                new.append([res[1], res[0]])
                table = Table(ref=res[0], name=res[1]) 
                table.save()
            """
        con.close()
        return new

    @classmethod
    def get_column_data(self):
        con = cx_Oracle.connect('username/password@server')
        tables = Table.objects.all()
        new = []
        for tt in tables:
            query = """SELECT column_name, data_type, data_length FROM ALL_TAB_COLUMNS WHERE table_name = '""" + tt.name + """' and OWNER = '""" + tt.ref + """'""" 
            cur = con.cursor()
            cur.execute(query)
            res_cols = ['name', 'type', 'length']
            rdata = cur.fetchall()
            data = pandas.DataFrame(rdata, columns=res_cols, index=range(0,len(rdata)))
            col_dat = data.to_json()
            if tt.data != col_dat:
                new.append([tt.ref, tt.name, col_dat])
                tt.data = col_dat
                tt.headers = json.dumps(res_cols)
                tt.save()
        con.close()
        return new

    @classmethod
    def cat_hist(self, ref, table, column):
        success = True
        new = []
        try:
            con = cx_Oracle.connect('username/password@server')
            query = """
            select
                tt."""+column+""" as val,
                count(*) as cnt
            from
                """+ref+"""."""+table+""" tt
            group by tt."""+column+"""
            order by tt."""+column+"""
            """
            cur = con.cursor()
            cur.execute(query)
            new = cur.fetchall()
            con.close()
            return success, 'success', [list(ii) for ii in new]
        except cx_Oracle.DatabaseError, exc:
            success = False
            error, = exc.args
            body = ""
            body += "Failed in finding categories for " + str(column)
            body += "<br>Oracle-Error-Code: " + str(error.code)
            body += "<br>Oracle-Error-Message: " + str(error.message)
            return success, body, []

    @classmethod
    def num_hist(self, ref, table, column, roundto, min_num, max_num):
        success = True
        new = []
        try:
            con = cx_Oracle.connect('username/password@server')
            try:
                int(roundto) # test if it is an integer
                query = """
                select
                    round(tt."""+column+""", """+roundto+""") as val,
                    count(*) as cnt
                from
                    """+ref+"""."""+table+""" tt
                where 1=1 """
                if not min_num == '':
                    query += """ and tt."""+column+""" >= """+min_num
                if not max_num == '':
                    query += """ and tt."""+column+""" <= """+max_num
                query += """ group by round(tt."""+column+""", """+roundto+""")"""
                query += """ order by round(tt."""+column+""", """+roundto+""")"""
            except:
                query = """
                select
                    tt."""+column+""" as val,
                    count(*) as cnt
                from
                    """+ref+"""."""+table+""" tt
                where 1=1 """
                if not min_num == '':
                    query += """ and tt."""+column+""" > """+min_num
                if not max_num == '':
                    query += """ and tt."""+column+""" < """+max_num
                query += """ group by tt."""+column
                query += """ order by tt."""+column
            cur = con.cursor()
            cur.execute(query)
            new = cur.fetchall()
            con.close()
            return success, 'success', [[str(ii[0]), ii[1]] for ii in new]
        except cx_Oracle.DatabaseError, exc:
            success = False
            error, = exc.args
            body = ""
            body += "Failed in finding numeric bins for " + str(column)
            body += "<br>Oracle-Error-Code: " + str(error.code)
            body += "<br>Oracle-Error-Message: " + str(error.message)
            return success, body, []

    @classmethod
    def date_hist(self, ref, table, column, min_date, max_date, roundto):
        success = True
        new = []
        try:
            # set the rounding
            if roundto == 'month':
                roundto = 'MON'
            elif roundto == 'day':
                roundto = 'DDD'
            elif roundto == 'week':
                roundto = 'WW'
            elif roundto == 'year':
                roundto = 'YYYY'
            else:
                roundto = 'MI'  # default is minute rounding
            con = cx_Oracle.connect('username/password@server')
            query = """
            select
                round(to_date(tt."""+column+"""), '"""+roundto+"""') as val,
                count(*) as cnt
            from
                """+ref+"""."""+table+""" tt
            where 1=1 """
            if not min_date == '':
                query += """ and ((cast("""+column+""" as date) - date '1970-01-01')*24*60*60) > """+min_date
            if not max_date == '':
                query += """ and ((cast("""+column+""" as date) - date '1970-01-01')*24*60*60) < """+max_date
            query += """ group by round(to_date(tt."""+column+"""), '"""+roundto+"""')"""
            query += """ order by round(to_date(tt."""+column+"""), '"""+roundto+"""')"""
            cur = con.cursor()
            cur.execute(query)
            new = cur.fetchall()
            con.close()
            return success, 'success', [[str(ii[0].date()), ii[1]] for ii in new if isinstance(ii[0], datetime)]
        except cx_Oracle.DatabaseError, exc:
            success = False
            error, = exc.args
            body = ""
            body += "Failed in finding date bins for " + str(column)
            body += "<br>Oracle-Error-Code: " + str(error.code)
            body += "<br>Oracle-Error-Message: " + str(error.message)
            return success, body, []


    def has_column(self, column):
        col_dat = pandas.io.json.read_json(self.data)
        if column in col_dat.name.tolist():
            return True
        return False

    def to_html(self):
        pheads = json.loads(self.headers)
        pdata = pandas.io.json.read_json(self.data)
        res = "<br><br><font color='blue'>" + self.ref + " . " + self.name + "</font><br>"
        res += "<table>"
        res += '<tr>'
        for hh in pheads:
            res += "<th align='left' style='padding: 0px 0px 0px 10px'>" + hh + "</th>"
        for row in pdata.iterrows():
            rdat = row[1]
            res += "<tr id='"+self.ref+","+self.name+","+str(row[1][1])+","+str(row[1][2])+"' class='context_table_column_data'>"
            for hh in pheads:
                res += "<td align='left' style='padding: 0px 0px 0px 10px'><nobr>" + str(rdat[hh]) + "</nobr></td>"
            res += '</tr>'
        res += '</table>'
        return res

class SampleFilter(models.Model):
    # [12m_to_SampleFilterPart]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='username') 
    name = models.CharField(max_length=50, null=True, blank=True)
    ref_table_column = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return str(self.id) + '_' + self.name 

class SampleFilterPart(models.Model):
    sample_filter = models.ForeignKey(SampleFilter, null=True) 
    ref = models.CharField(max_length=50, null=True, blank=True)
    table = models.CharField(max_length=100, null=True, blank=True)
    filter_col = models.CharField(max_length=100, null=True, blank=True)
    ftype = models.CharField(max_length=50, blank=True, null=True)
    cats = models.TextField(null=True, blank=True) # json array of selected categories

    def Get_Cats(self):
        try: 
            ret = json.loads(self.cats)
            if isinstance(ret, list):
                return ret
        except:
            pass
        return []
        
    def Set_Cats(self, cats):
        self.cats = json.dumps(cats)
        self.save()
   
    def Add_Cats(self, val):
        cats = self.Get_Cats() 
        cats.append(val)
        self.Set_Cats(cats)

    def Cat_Choices(self):
        new = self.Get_Cats()
        #ids = ['_'.join(['id', ii[0]]) for ii in new]
        ids = [ii[0] for ii in new]
        choices = [' : '.join(["'"+ii[0]+"'", str(ii[1])]) for ii in new]
        return zip(ids, choices)

    def Retrieve_Cats(self):
        try:
            con = cx_Oracle.connect('username/password@server')
            query = """
            select
                tt."""+self.filter_col+""" as cat,
                count(*) as cnt
            from
                """+self.ref+"""."""+self.table+""" tt"""
            query += """ group by tt."""+self.filter_col
            query += """ order by tt."""+self.filter_col
            cur = con.cursor()
            cur.execute(query)
            new = cur.fetchall()
            con.close()
            self.Set_Cats(new)
            return "Success adding filter and categories for " + str(self.filter_col) 
        except cx_Oracle.DatabaseError, exc:
            error, = exc.args
            body = ""
            body += "Failed adding filter and categories for " + str(self.filter_col)
            body += "\nOracle-Error-Code: " + str(error.code)
            body += "\nOracle-Error-Message: " + str(error.message)
            return body
   
SAMPLE_STATUS_CHOICES = (
    ('Empty', 'Empty'),
    ('Active', 'Active'),
    ('Loaded', 'Loaded'),
    ('Failed', 'Failed'),
)

class Sample(models.Model):
    # [12m_to_SProperty]
    # [12m_to_OSample]
    # [12m_to_Report]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='username') 
    name = models.CharField(max_length=50, null=True, blank=True)
    stype = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=30, default='Empty', choices=SAMPLE_STATUS_CHOICES)
    detail = models.TextField(null=True, blank=True)
    key_column = models.CharField(max_length=100, null=True, blank=True)
    
    def __unicode__(self):
        nos = len(self.osample_set.all())
        return str(self.id) + '_' + self.name + ' - ' + str(nos)

    @classmethod
    def add(self, user, pks, sample_name, key_col, stype, detail=None):
        sample = Sample(user=user, name=sample_name, stype=stype, key_column=key_col, detail=detail) 
        sample.save()
        for fk in pks:
            so = OSample(sample=sample, oid=fk.strip()) 
            so.save()

    def osamples_total(self):
        return [oo for oo in self.osample_set.all()]

    def osamples_retrieved(self):
        pass
        #return [oo for oo in self.osample_set.all() if not oo.retrieved is None]
    
    def osamples_percent(self):
        pass
        """
        retrieved = len(self.osamples_retrieved())
        total = len(self.osamples_total())
        if total == 0:
            return 0
        else:
            return int(float(retrieved) / float(total) * 100)
        """

    @classmethod
    def retrieve(self, who, sid, link):
        sample = Sample.objects.get(pk=sid)
        # the only state that' makes sense to start retrieving data from is 'Empty'
        if not sample.status in ['Empty', 'Failed']:
            return
        sample.status = 'Active'
        sample.save()
        # filter possible tables
        try:
            con = cx_Oracle.connect('username/password@server')
            tables = Table.objects.all()
            filter1 = []
            filter2 = []
            for tt in tables:
                if tt.has_column(sample.key_column):
                    filter1.append(tt)
            for tt in filter1:
                if not tt.name.startswith("ADSNAP_"):
                #if tt.name.startswith("PERSONAL_PHONE"):
                #if tt.name.startswith("ADM_APPL_PROG") or tt.name.startswith("EXT_ACAD_SUM"):
                    filter2.append(tt)
            possible_tables = filter2
            # delete all the 'old' results first
            Result.objects.filter(osample__sample=sample).delete()
            # look in all possible tables for all possible students
            nn = 1000 # max size for sql 'in (...)' clause
            osamples = sample.osample_set.all()
            osample_chunks = [osamples[i:i+nn] for i in range(0, len(osamples), nn)]
            combo_result_sets = []
            for os_chunk in osample_chunks:
                os_pks = [ss.oid for ss in os_chunk]
                for tt in possible_tables:
                    query = "select * from " + tt.ref + "." + tt.name + " where " + " EMPLID='" + "' or EMPLID='".join(os_pks) + "'"
                    cur = con.cursor()
                    cur.execute(query)
                    res = cur.fetchall()
                    retrieved_at = datetime.now(tz=timezone('America/Detroit'))
                    #print 'STUFFING', tt.ref, '.', tt.name
                    if cur.rowcount > 0:
                        tpl_cols = zip(*cur.description)[0]
                        arr_cols = [x for x in tpl_cols]
                        pres = pandas.DataFrame(res, columns=arr_cols, index=range(0,len(res)))
                        rs = [tt.ref, tt.name, json.dumps(arr_cols), pres]
                        # distribute result sets back to individual students
                        rso_stash = []
                        for oo in os_chunk:
                            sub = []
                            sub = rs[3][rs[3][sample.key_column] == oo.oid]
                            rso = Result(osample=oo, ref=rs[0], table=rs[1])
                            rso.headers=rs[2]
                            rso.retrieved = retrieved_at
                            if len(sub) > 0:
                                rso.data=sub.to_json(date_format='iso')
                                rso_stash.append(rso)
                        Result.objects.bulk_create(rso_stash)
            # set to finished if done
            sample.status = 'Loaded'
            sample.save()
            body = ""
            body += "Retrieving the sample identified by '" + str(sample.id) + "_" + str(sample.name) + "' was successful!<br>"
            body += "Browse the results here: <a href='"+link+"'>"+link+"</a><br>"
        except cx_Oracle.DatabaseError, exc:
            error, = exc.args
            #print "Oracle-Error-Code:", error.code
            #print "Oracle-Error-Message:", error.message
            body = ""
            body += "Retrieving the sample with id " + str(sample.id) + " and name " + str(sample.name) + "' failed!<br>"
            body += "Oracle-Error-Code: " + str(error.code)
            body += "<br>"
            body += "Oracle-Error-Message: " + str(error.message)
            sample.status = 'Failed'
            sample.save()
        con.close()
        # email user the errors or success message!!!
        Sample.send_email(who, body)

    @classmethod
    def send_email(self, to_who, body):
        # message settings
        sentfrom = 'username@domain.edu'
        sendto = [to_who+'@domain.edu']
        bcc = [] #self.bcc_query.get_bcc()
        subject = 'Transfer App - Status Update' #self.subject 
        bodytext = 'html message'
        html_content = body #self.body
        # use the settings
        message = EmailMultiAlternatives(
            subject, 
            bodytext, 
            sentfrom,
            sendto, 
            bcc, 
            headers = {'Reply-To': 'username@domain.edu'}
        )
        message.attach_alternative(html_content, "text/html")
        try:
            message.send()
        except:
            pass # in development this needs to fail

    #:::::::::::::::::::::::::::::::::::::::#
    # Dynamic Sample Reporting Methods
    #:::::::::::::::::::::::::::::::::::::::#

    def table_column_distribution(self, ref, table, column):
        sample_objs = self.osample_set.all()
        results = []
        scol = pandas.Series()
        for so in sample_objs:
            #results = so.result_set.filter(ref=ref, table=table).exclude(data=None)
            results = so.result_set.filter(ref=ref, table=table)
            if len(results) > 0: # should only be one
                data = pandas.io.json.read_json(results[0].data)
                pp = data.loc[:,column]
                scol = scol.append(pp)
        aa = scol.value_counts()
        lpairs = [[str(ii) for ii in aa.index.tolist()], aa.values.tolist()]
        return [list(ii) for ii in zip(*lpairs)]

    #:::::::::::::::::::::::::::::::::::::::#
    # Dynamic OSample Reporting Methods
    #:::::::::::::::::::::::::::::::::::::::#

    def table_column_num_entries(self, ref, table, column):
        sample_objs = self.osample_set.all()
        results = []
        rdata = []
        for so in sample_objs:
            #results = so.result_set.filter(ref=ref, table=table).exclude(data=None)
            results = so.result_set.filter(ref=ref, table=table)
            if len(results) > 0: # should only be one
                rdata.append(len(pandas.io.json.read_json(results[0].data)))
            else:
                rdata.append(0)
        vals = sorted(set(rdata))
        lpairs = []
        for vv in vals:
            lpairs.append([str(vv), rdata.count(vv)]) 
        return lpairs

    #:::::::::::::::::::::::::::::::::::::::#
    # Property Reporting Methods
    #:::::::::::::::::::::::::::::::::::::::#

    def sync_properties(self):
        properties = [ 
            # dictionary map for property managment
            # HACK-ALERT be cautious not to delete methods without deleting SProperty objects in DB
            # ['method', 'vtype', 'label'] (label is mutable)
            # APPLYING STUDENTS
                # NUMERICS
                ['calc_table_count', 'Int', 'Number of tables'],
                ['calc_graduated', 'Int', 'Graduated'],
                ['calc_graduated_new', 'Int', 'Graduated New'],
                ['first_year_applied','Int', 'First Year Applied'],
                #['semester_applied', 'Float', 'Semester Applied'],
                ['high_school_gpa', 'Float', 'High School GPA'],
                #['overall_sat', 'Int', 'Overall SAT Score'],
                #['overall_act', 'Int', 'Overall ACT Score'],
                #['ap_placement_credits', 'Int', 'Advanced Placement Credits'],
                #['apps_denied', 'Int', 'Applications Denied'],
                ['trans_undergrad_gpa', 'Float', 'Transfer - Undergrad GPA'],
                #['trans_num_courses', 'Int', 'Transfer - Number Courses'],
                #['trans_num_credits', 'Int', 'Transfer - Number Credits'],
                # CATS
                ['first_career_applied', 'String', 'First Career Applied'],
                ['domestic_student', 'String', 'Domestic or International'],
                ['international_student', 'String', 'International Origin'],
                ['in_state', 'String', 'In or Out of State'],
                #['urop_student', 'String', 'UROP Participation'],
                #['transfer_status', 'String', 'Transfer Status'], <<< not useful yet... only useful if dependency issues resolved so properties can depend on other properties
            # MATRICULATED STUDENTS
                # NUMERICS
                #['year_started', 'Int', 'Year Started'],
                #['year_graduated', 'Int', 'Year Graduated'],
                #['semester_started', 'Float', 'Semester Started'],
                #['semester_graduated', 'Float', 'Semester Graduated'],
                ['semesters_to_graduate_new', 'Int', 'Semesters to Graduate New'],
                ['avg_tuition_amt', 'Int', 'Avg of Tution Amount'],
                #['graduation_overall_gpa', 'Float', 'Graduation GPA - Overall'],
                ['avg_semester_gpa', 'Float', 'Avg Semster GPA'],
                #['number_changes_to_plan', 'Int', 'Number of Changes to Plan'],
                #['months_to_first_plan_change', 'Int', 'Months to First Plan Change'],
                #['num_credits_from_um', 'Int', 'Number of Credits From UM'],
                # CATS
                #['graduation_status', 'String', 'Graduation Status'],
                ['start_career', 'String', 'Starting Career'],
                ['start_plan', 'String', 'Starting Plan'],
                ['graduation_career', 'String', 'Graduation Career'],
                ['graduation_plan', 'String', 'Graduation Plan'],
                ['parents_education', 'String', 'Parents Level of Education'],
                ['family_income', 'String', 'Family Income'],
                #['app_final_eval', 'Int', 'Application Final Evaluation Score'],
                #['', '', ''],
                # how many courses in TRNS_CRSE_DTL?  how many grading schemes?
                # most common grading scheme?  which careers are they transferring credit to?
                # 
                # 
                # 
                # 
        ] 

        """
        http://pandas.pydata.org/pandas-docs/stable/merging.html#brief-primer-on-merge-methods-relational-algebra
        join takes an optional on argument which may be a column or multiple column names, 
        which specifies that the passed DataFrame is to be aligned on that column in the DataFrame. 
        These two function calls are completely equivalent:
            left.join(right, on=key_or_keys)
            merge(left, right, left_on=key_or_keys, right_index=True, how='left', sort=False)
        """
        for pp in properties:
            print pp[0]
            sprop = SProperty.objects.get_or_create(sample=self, method=pp[0])[0]
            # alwasy update vtype and label to match dictionary, including first time
            if sprop.vtype != pp[1] or sprop.label != pp[2]:
                sprop.vtype = pp[1]
                sprop.label = pp[2]
                sprop.save()

    @classmethod
    def calculate_properties(self, sample_property_ids, who, email):
        sproperties = SProperty.objects.filter(id__in=sample_property_ids)
        # sproperties is list of ORM objects!!
        for sp in sproperties: # avoid starting to calc if already active
            # HACK-ALERT False here for debugging only!!!!...though it's handy this way???
            #if sp.status == "Active" or sp.status == "Loaded": 
            if False: 
                sproperties.remove(sp) 
        if len(sproperties) == 0: # avoid wasting time...
            return
        sample = sproperties[0].sample # they are all the same
        # quick set sproperties to active
        for sp in sproperties:
            sp.status = "Active"
            sp.save()
        # calc the new properties
        # delete all OProperty and Error objects for outer product of osamples X sproperties
        OProperty.objects.filter(osample__sample=sample, sproperty__in=sproperties).delete()
        Error.objects.filter(sproperty__in=sproperties).delete()
        osamples = sample.osample_set.all()
        oprop_cache = []
        error_cache = []
        for os in osamples:
            oprops, errors = os.calc_properties(sproperties)
            oprop_cache += oprops
            error_cache += errors
            if len(oprop_cache) > 1000:
                OProperty.objects.bulk_create(oprop_cache)
                oprop_cache = []
            if len(error_cache) > 1000:
                Error.objects.bulk_create(error_cache)
                error_cache = []
        OProperty.objects.bulk_create(oprop_cache)  # pick up last of cache
        Error.objects.bulk_create(error_cache)      # save last of sproperty error messages
        # set status of each sproperty to loaded
        for sp in sproperties:
            sp.status = "Loaded"
            sp.save()
        # email notification
        if email == 'yes':
            body = ""
            body += "Finished calculating properties for sample with id " + str(sample.id) + " and name " + str(sample.name) + "!<br>Properties:"
            for sp in sproperties:
                body += " ".join(["<br>", sp.label])
            Sample.send_email(who, body)

SAMPLE_PROPERTY_STATUS_CHOICES = (
    ('Empty', 'Empty'),
    ('Active', 'Active'),
    ('Loaded', 'Loaded'),
    ('Failed', 'Failed'),
)

VALUE_TYPE_CHOICES = (
    ('Int', 'Int'),
    ('Float', 'Float'),
    ('String', 'String'),
)

class SProperty(models.Model):
    # [12m_to_OProperty]
    # [12m_to_ComarisonA] x 2
    # [12m_to_Error]
    # bascially cache data about OProperty sets for a sample
    sample = models.ForeignKey(Sample, null=True)
    label = models.CharField(max_length=200, null=True, blank=True)
    method = models.CharField(max_length=200, null=True, blank=True)
    vtype = models.CharField(max_length=30, default='String', choices=VALUE_TYPE_CHOICES)
    status = models.CharField(max_length=30, default='Empty', choices=SAMPLE_PROPERTY_STATUS_CHOICES)
    
class OSample(models.Model):
    # [12m_to_OProperty]
    # [12m_to_Result]
    sample = models.ForeignKey(Sample, null=True)
    oid = models.CharField(max_length=50, null=True, blank=True)

    def calc_properties(self, sproperties):
        #results = Result.objects.filter(osample=self)  
        results = self.result_set.all()
        oprop_cache = []
        error_cache = []
        for sp in sproperties:
            # calc the property
            val = None
            if hasattr(self, sp.method):
                try:
                    val = getattr(self, sp.method)(results)
                    if val != None: # no need to make null properties, non-existent is same as null
                        oprop_cache.append(OProperty(osample=self, sproperty=sp, value=val))
                except:
                    msg = ' '.join(['Error calculating: "', sp.label, '" for ', self.oid])
                    error_cache.append(Error(sproperty=sp, message=msg))
        return oprop_cache, error_cache

    def calc_table_count(self, results):
        cnt = 0
        for rr in results:
            cnt += 1
        return cnt

    def calc_graduated(self, results):
        res = None
        graduated = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='ACAD_PROG':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            graduated = 0
            sub = data[data['ACAD_CAREER'].str.startswith('U')] 
            if len(sub) > 0:
                if 'Completed' in sub['PROG_STATUS_DESCRSHORT'].values:
                    graduated = 1
        return graduated

    def calc_graduated_new(self, results):
        res_ACAD_DEGR = None
        res_STDNT_ENRL = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='ACAD_DEGR':
                res_ACAD_DEGR = rr
                break
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='STDNT_ENRL':
                res_STDNT_ENRL = rr
                break
        graduated = None
        if res_STDNT_ENRL != None:
            graduated = 0
            if res_ACAD_DEGR != None:
                data = pandas.io.json.read_json(res_ACAD_DEGR.data)
                sub = data[data['ACAD_CAREER'].str.startswith('U')] 
                if len(sub) > 0:
                    graduated = 1
        return graduated

    def first_year_applied(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_RADW1' and rr.table=='ADM_APPL_DATA':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            data = data[data['ADM_APPL_CTR_DESCRSHORT']=='Ugrad Adm']
            data = data[data['ADM_APPL_COMPLETE']=='Y']
            # double check is date since some don't have dates
            if len(data) > 0 and data['ADM_APPL_CMPLT_DT'].dtype == 'O': 
                data.sort('ADM_APPL_CMPLT_DT', ascending=True, inplace=True) # most recent
                dat = data.iloc[0]['ADM_APPL_CMPLT_DT'].rstrip('000Z').rstrip('.') # may have this
                ret = datetime.strptime(dat, '%Y-%m-%dT%H:%M:%S').year
        return ret

    def high_school_gpa(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='EXT_ACAD_SUM':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            # filter to those that have undergrad gpa from external org
            data = data[data['EXT_CAREER']=='HS']
            if len(data) > 0: # usually only one...but this handles edge cases
                ret = str(round(data[:]['CONVERT_GPA'].mean(),2))
        return ret 

    def trans_undergrad_gpa(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='EXT_ACAD_SUM':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            # filter to those that have undergrad gpa from external org
            data = data[data['EXT_CAREER']=='UGRD']
            if len(data) > 0: # usually only one...but this handles edge cases
                ret = str(round(data[:]['CONVERT_GPA'].mean(),2))
        return ret 

    def in_state(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='RESIDENCY_OFF':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            data.sort('EFFECTIVE_TERM', ascending=True, inplace=True)
            ret = str(data.iloc[0]['RESIDENCY'])
        return ret

    def semesters_to_graduate(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='STDNT_CAR_TERM':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            if len(data) > 0: # usually only one...but this handles edge cases
                # filter on first letter U in ACAD_CAREER
                sub = data[data['ACAD_CAREER'].str.startswith('U')] 
                ret = len(sub.groupby('TERM'))
        return ret 

    def semesters_to_graduate_new(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='STDNT_CAR_TERM':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            if len(data) > 0: # usually only one...but this handles edge cases
                # filter on first letter U in ACAD_CAREER
                sub = data[data['ACAD_CAREER'].str.startswith('U')] 
                fall = sub[sub['TERM_DESCRSHORT'].str.startswith('FA')] 
                winter = sub[sub['TERM_DESCRSHORT'].str.startswith('WN')] 
                ret = len(winter) + len(fall)
                #ret = len(winter.append(fall).groupby('TERM'))
        return ret 



    def avg_tuition_amt(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='STDNT_CAR_TERM':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            # filter to those that have undergrad gpa from external org
            if len(data) > 0: # usually only one...but this handles edge cases
                ret = str(round(data[:]['TUITION_AMT'].mean(),-3))
        return ret 

    def avg_semester_gpa(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='STDNT_CAR_TERM':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            sub = data[(data['ACAD_CAREER'].str.startswith('U')) & (data['REG_STATUS'] == 'RGSD')] 
            if len(sub) > 0: # usually only one...but this handles edge cases
                # filter on first letter U in ACAD_CAREER
                ret = str(round(data[:]['CUR_GPA'].mean(),2))
        return ret 

    def domestic_student(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='PERSONAL_DATA':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            # one entry per student, it seems
            ret = str(data.iloc[0]['CITIZENSHIP_COUNTRY1_DESCR'])
        return ret

    def international_student(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_SRDW1' and rr.table=='PERSONAL_DATA':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            sub = data[(data['CITIZENSHIP_COUNTRY1_DESCR'] != 'United States')] 
            if len(sub) > 0:
                # one entry per student, it seems
                ret = str(data.iloc[0]['CITIZENSHIP_COUNTRY1_DESCR'])
        return ret

    def first_career_applied(self, results):
        res = None
        ret = None
        for rr in results:
            # only one result table is important
            if rr.ref=='M_RADW1' and rr.table=='ADM_APPL_DATA':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            # one entry per student, it seems
            data.sort('ADM_APPL_CMPLT_DT', ascending=True, inplace=True)
            ret = str(data.iloc[0]['ACAD_CAREER_DESCRSHORT'])
        return ret

    def graduation_career(self, results):
        res = None
        ret = None
        for rr in results:
            if rr.ref=='M_SRDW1' and rr.table=='STDNT_CAR_TERM':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            sub = data[(data['ACAD_CAREER'].str.startswith('U')) & (data['REG_STATUS'] == 'RGSD')] 
            if len(sub) > 0: 
                sub.sort('TERM', ascending=False, inplace=True)
                ret = str(sub.iloc[0]['ACAD_CAREER_DESCRSHORT'])
        return ret

    def start_plan(self, results):
        res = None
        ret = None
        for rr in results:
            if rr.ref=='M_SRDW1' and rr.table=='STDNT_CAR_TERM':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            sub = data[(data['ACAD_CAREER'].str.startswith('U')) & (data['REG_STATUS'] == 'RGSD')] 
            if len(sub) > 0: 
                sub.sort('TERM', ascending=True, inplace=True)
                ret = str(sub.iloc[0]['ACAD_PLAN_PRIMARY_DESCR'])
        return ret

    def graduation_plan(self, results):
        res = None
        ret = None
        for rr in results:
            if rr.ref=='M_SRDW1' and rr.table=='STDNT_CAR_TERM':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            sub = data[(data['ACAD_CAREER'].str.startswith('U')) & (data['REG_STATUS'] == 'RGSD')] 
            if len(sub) > 0: 
                sub.sort('TERM', ascending=False, inplace=True)
                ret = str(sub.iloc[0]['ACAD_PLAN_PRIMARY_DESCR'])
        return ret

    def parents_education(self, results):
        res = None
        ret = None
        for rr in results:
            if rr.ref=='M_RADW1' and rr.table=='ADM_APPL_EVAL':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            sub = data[(data['RATING_CMP_DESCRSHORT'] == 'PrntLvlEd')] 
            # RATING_CMP_VALUE_DESCR 
            if len(sub) > 0: 
                ret = str(sub.iloc[0]['RATING_CMP_VALUE_DESCR'])
        return ret

    def family_income(self, results):
        res = None
        ret = None
        for rr in results:
            if rr.ref=='M_RADW1' and rr.table=='ADM_APPL_EVAL':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            sub = data[(data['RATING_CMP_DESCRSHORT'] == 'EstGrossIn')] 
            # RATING_CMP_VALUE_DESCR 
            if len(sub) > 0: 
                ret = str(sub.iloc[0]['RATING_CMP_VALUE_DESCR'])
        return ret

    def app_final_eval(self, results):
        res = None
        ret = None
        for rr in results:
            if rr.ref=='M_RADW1' and rr.table=='ADM_APPL_EVAL':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            sub = data[(data['RATING_CMP_DESCRSHORT'] == 'Final Eval')] 
            sub = sub[sub['RATING_CMP_VALUE'].map(np.isreal)]
            # RATING_CMP_VALUE_DESCR 
            if len(sub) > 0: 
                # most have multiple raters
                ret = str(round(sub['RATING_CMP_VALUE_DESCR'].mean(),0))
                print len(sub), ret
                import pdb; pdb.set_trace() 
        return ret

    def start_career(self, results):
        res = None
        ret = None
        for rr in results:
            if rr.ref=='M_SRDW1' and rr.table=='STDNT_CAR_TERM':
                res = rr
                break
        if res != None:
            data = pandas.io.json.read_json(res.data)
            sub = data[(data['ACAD_CAREER'].str.startswith('U')) & (data['REG_STATUS'] == 'RGSD')] 
            if len(sub) > 0: 
                sub.sort('TERM', ascending=True, inplace=True) 
                ret = str(sub.iloc[0]['ACAD_CAREER_DESCRSHORT'])
        return ret

class OProperty(models.Model):
    osample = models.ForeignKey(OSample, null=True)
    sproperty = models.ForeignKey(SProperty, null=True)
    value = models.CharField(max_length=200, null=True, blank=True)

class Result(models.Model):
    osample = models.ForeignKey(OSample, null=True)
    table = models.CharField(max_length=100, null=True, blank=True)
    ref = models.CharField(max_length=50, null=True, blank=True)
    headers = models.TextField(null=True, blank=True) # json 
    data = models.TextField(null=True, blank=True) # json 
    retrieved = models.DateTimeField(auto_now=False,blank=True, null=True)

    def to_html(self):
        pheads = json.loads(self.headers)
        pdata = pandas.io.json.read_json(self.data)
        res = []
        res.append("<br><br><font id='"+self.ref+","+self.table+"' class='context_result_table' color='blue'>" + self.ref + " . " + self.table + "</font><br>")
        res.append("<table>")
        res.append('<tr>')
        for hh in pheads:
            res.append("<th id='"+self.ref+","+self.table+","+hh+"' class='context_result_column' align='left' style='padding: 0px 0px 0px 10px'>" + hh + "</th>")
        for row in pdata.iterrows():
            rdat = row[1]
            res.append("<tr>")
            for hh in pheads:
                res.append("<td id='"+self.ref+","+self.table+","+hh+","+str(rdat[hh])+"' class='context_result_data' align='left' style='border-right: solid; padding: 0px 10px 0px 10px'><nobr>" + str(rdat[hh]) + "</nobr></td>")
            res.append('</tr>')
        res.append('</table>')
        return ''.join(res)

class Comparison(models.Model):
    # [121_to_Report]
    spropertyA = models.ForeignKey(SProperty, related_name='spropA')
    spropertyB = models.ForeignKey(SProperty, related_name='spropB')
    label = models.CharField(max_length=200, null=True, blank=True)
    method = models.CharField(max_length=200, null=True, blank=True)
  
    @classmethod 
    def sync_comparisons(self, sprops):
        comparisons = [ 
            # dictionary map for property managment
            # HACK-ALERT be cautious not to delete methods without deleting SProperty objects in DB
            # ['method', 'label'] (label is mutable)
            #['normal_hist_dist', 'Normalized Histograms'],
            #['normal_cumulative_dist', 'Normalized Cumulatives'],
            ['normalized_distributions', 'Normalized Distributions'],
        ] 
        for cc in comparisons:
            for sp in sprops:
                if sp[0].id == sp[1].id:
                    continue
                comp = Comparison.objects.get_or_create(spropertyA=sp[0], spropertyB=sp[1], method=cc[0])[0]
                # alwasy update label to match dictionary, including first time
                if comp.label != cc[1]:
                    comp.label = cc[1]
                    comp.save()

    def has_report(self):
        if self.report_set.count() == 0:
            return ''
        return 'has-report'

    @classmethod 
    def calculate_comparisons(self, who, comp_ids):
        comps = [Comparison.objects.get(id=ii) for ii in comp_ids]
        for comp in comps:
            comp.make_comparisons(who, comp)

    def make_comparisons(self, who, comp):
        adata = [pp.value for pp in comp.spropertyA.oproperty_set.all()]
        bdata = [pp.value for pp in comp.spropertyB.oproperty_set.all()]
        if hasattr(comp, comp.method):
            getattr(comp, comp.method)(who, adata, bdata)

    def normalized_distributions(self, who, adata, bdata):
        from django.template.loader import render_to_string
        from django.contrib.auth import get_user_model
        import inspect
        user = get_user_model().objects.get(username=who)
        # HISTOGRAM
        # bin the data
        aseries = pandas.Series(adata)
        bseries = pandas.Series(bdata)
        ahist = aseries.value_counts(normalize=True).sort_index()
        bhist = bseries.value_counts(normalize=True).sort_index()
        # make sure there is a shared index for display purposes
        mkeys = [ii for ii in set(ahist.index + bhist.index)]
        # create an array from these series using dictionary
        pdict = dict((k, [str(k), 0, 0]) for k in mkeys)
        for aa in ahist.iteritems():
            pdict[aa[0]][1] = aa[1]
        for bb in bhist.iteritems():
            pdict[bb[0]][2] = bb[1]
        hist_pairs = []
        for ii in pdict:
            dat = pdict[ii]
            hist_pairs.append([dat[0], round(dat[1], 4), round(dat[2], 4)])
        if self.spropertyA.vtype == 'Int':
            hist_pairs = sorted(hist_pairs, key=lambda x: int(float(x[0])), reverse=False)
        elif self.spropertyA.vtype == 'Float':
            hist_pairs = sorted(hist_pairs, key=lambda x: float(x[0]), reverse=False)
        else:
            hist_pairs = sorted(hist_pairs, key=lambda x: x[0], reverse=False)
        # CUMULATIVE
        # bin the data for cum 
        # handle by type
        aseries = pandas.Series(adata)
        ahist = aseries.value_counts(normalize=True)
        if self.spropertyA.vtype == 'Int':
            aindex = [int(float(ii)) for ii in ahist.index]
        elif self.spropertyA.vtype == 'Float':
            aindex = [float(ii) for ii in ahist.index]
        else:
            aindex = [ii for ii in ahist.index]
        aps = pandas.Series(ahist.values, index=aindex)
        adone = aps.sort_index().cumsum()
        # handle by type
        bseries = pandas.Series(bdata)
        bhist = bseries.value_counts(normalize=True)
        if self.spropertyA.vtype == 'Int':
            bindex = [int(float(ii)) for ii in bhist.index]
        elif self.spropertyA.vtype == 'Float':
            bindex = [float(ii) for ii in bhist.index]
        else:
            bindex = [ii for ii in bhist.index]
        bps = pandas.Series(bhist.values, index=bindex)
        bdone = bps.sort_index().cumsum()
        # make sure there is a shared index for display purposes
        mkeys = [ii for ii in set(adone.index + bdone.index)]
        for kk in mkeys:
            if not kk in bdone.index:
                bdone.set_value(kk,0)
            if not kk in adone.index:
                adone.set_value(kk,0)
        # inserted indexes are 0, so now match them to prev index
        prev_val = 0
        for vv in adone.sort_index().iteritems():
            if vv[1] < prev_val:
                adone[vv[0]] = prev_val
            else:
                prev_val = vv[1]
        prev_val = 0
        for vv in bdone.sort_index().iteritems():
            if vv[1] < prev_val:
                bdone[vv[0]] = prev_val
            else:
                prev_val = vv[1]
        # create an array from these series using dictionary
        pdict = dict((k, [str(k), 0, 0]) for k in mkeys)
        for aa in adone.iteritems():
            pdict[aa[0]][1] = aa[1]
        for bb in bdone.iteritems():
            pdict[bb[0]][2] = bb[1]
        cum_pairs = []
        for ii in pdict:
            dat = pdict[ii]
            cum_pairs.append([dat[0], round(dat[1], 4), round(dat[2], 4)])
        if self.spropertyA.vtype == 'Int':
            cum_pairs = sorted(cum_pairs, key=lambda x: int(float(x[0])), reverse=False)
        elif self.spropertyA.vtype == 'Float':
            cum_pairs = sorted(cum_pairs, key=lambda x: float(x[0]), reverse=False)
        else:
            cum_pairs = sorted(cum_pairs, key=lambda x: x[0], reverse=False)
        # render django template
        plot_xlab = 'Property: ' + self.spropertyA.label
        plot_ylab = ''
        osample = self.spropertyA.sample.osample_set.all()[:1].get()
        code_calc = '    # Calculation for each element of the sample\n'
        if hasattr(osample, self.spropertyA.method):
            code_calc += inspect.getsource(getattr(osample, self.spropertyA.method))
        sampleA_label = str(self.spropertyA.sample)
        sampleB_label = str(self.spropertyB.sample)
        resp = render_to_string('myexplorer/comparison_distributions.html', {
            'code_calc': code_calc,
            'plot_xlab': plot_xlab,
            'plot_ylab': plot_ylab,
            'sampleA_label': sampleA_label,
            'sampleB_label': sampleB_label,
            'numA': self.spropertyA.oproperty_set.count(),
            'numB': self.spropertyB.oproperty_set.count(),
            'errorsA': Error.objects.filter(sproperty=self.spropertyA),
            'errorsB': Error.objects.filter(sproperty=self.spropertyB),
            'plot_pairs_norm': hist_pairs,
            'plot_pairs_cum': cum_pairs,
            'plot_pairs_both': zip(hist_pairs, cum_pairs)
        })
        # create report object
        Report.objects.filter(comparison=self).delete()
        report = Report(user=user, created=datetime.now(), rtype='analysis', comparison=self)
        report.save()
        # save the html to file
        ofile = settings.HTML_ROOT + str(report.id) + '_report.html'
        htmlstr = resp
        Html_file= open(ofile,"w")
        Html_file.write(htmlstr)
        Html_file.close

class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='username', null=True) 
    name = models.CharField(max_length=200, blank=True, null=True)
    comparison = models.ForeignKey(Comparison, null=True)
    sample = models.ForeignKey(Sample, null=True)
    created = models.DateTimeField(auto_now=False,blank=True, null=True)
    rtype = models.CharField(max_length=50, blank=True, null=True)
    tags = models.TextField(null=True, blank=True) # comma seperated
    # cache the goodies 

    def get_link(self):
        return str(self.id) + '_report.html'

class Error(models.Model):
    sproperty = models.ForeignKey(SProperty, null=True)
    message = models.CharField(max_length=500, null=True, blank=True)


