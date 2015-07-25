from django import forms
from .models import *
from django.forms.util import ErrorList

class Fixed_Ids_Upload_Form(forms.Form):
    sample_name = forms.CharField(
        label='Please name this sample', 
        max_length=50, 
        required=True, 
        error_messages={'required': 'You must name the sample'}
    )
    sample_key_column = forms.CharField(
        label='For reference enter sample key column', 
        max_length=50, 
        required=True, 
        error_messages={'required': 'example: EMPLID'}
    )
    csv_file = forms.FileField(label='Select a file', required=True, error_messages={'required': 'You must choose a file with ids one per line'})

class Sub_Sample_Form(forms.Form):
    sample = forms.ModelChoiceField(
        required=True, 
        label='Select a starting sample', 
        error_messages={'required': 'You must choose a sample'},
        queryset=Sample.objects.all().order_by('-id'), 
        widget=forms.Select(attrs={"onChange":"$('form').submit();"})
    )
    sub_size = forms.IntegerField(
        label='New sample size', 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder':"size...", 'class':'input-large'})
    )
    sub_name = forms.CharField(
        max_length=50, 
        label='New sample name', 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder':"name...", 'class':'input-large'})
    )
    def clean(self):
        if 'sample' in self.cleaned_data.keys() and 'sub_size' in self.cleaned_data.keys():
            olds = OSample.objects.filter(sample=self.cleaned_data['sample'])
            if self.cleaned_data['sub_size'] > len(olds):
                self._errors['sub_size'] = ErrorList(["Can not be bigger than starting sample size"])
        return self.cleaned_data
  
class Browse_Sample_Data_Form(forms.Form):
    sample = forms.ChoiceField(
        required=False
    )

    def __init__(self, choices, *args, **kwargs):
        super(Browse_Sample_Data_Form, self).__init__(*args, **kwargs)
        self.fields['sample'].choices = choices

class Retrieve_Schema_Form(forms.Form):
    trigger = forms.MultipleChoiceField(
        required=True, 
        widget=forms.CheckboxSelectMultiple,
        choices=(('trigger', "Yes, I'm sure, (takes about 10 minutes!)"),)
    )

class Filter_Select_Form(forms.Form):
    sfilter = forms.ModelChoiceField(
        required=True, 
        label='Select a Filter', 
        queryset=SampleFilter.objects.all().order_by('-id'), 
        widget=forms.Select(attrs={'onchange': "$('#theform').submit();"})
    )

class Sample_Filter_Cat_Form(forms.ModelForm):
    categories = forms.MultipleChoiceField(
        required=False, 
        widget=forms.SelectMultiple(attrs={'style': 'width:100%'}), 
        label=''
        )

    class Meta:
        model = SampleFilterPart
        fields = []

    def __init__(self, *args, **kwargs):
        super(Sample_Filter_Cat_Form, self).__init__(*args, **kwargs)
        self.fields['categories'].choices = self.instance.Cat_Choices()

    def label(self):
        mod = self.instance
        return ' . '.join([mod.ref, mod.table, mod.filter_col])

class Sample_Filter_Num_Form(forms.ModelForm):
    min_num = forms.CharField(
        max_length=50, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder':"min: number", 'class':'input-large'}),
        error_messages={'invalid': 'Please enter a number'}
    )
    max_num = forms.CharField(
        max_length=50, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder':"max: number", 'class':'input-large'}),
        error_messages={'invalid': 'Please enter a number'}
    )

    class Meta:
        model = SampleFilterPart
        fields = []

    def label(self):
        mod = self.instance
        return ' . '.join([mod.ref, mod.table, mod.filter_col])

    def clean_min_num(self):
        if self.cleaned_data['min_num'] == '':
            return ''
        try:
            return float(self.cleaned_data['min_num'])
        except:
            raise forms.ValidationError(self.fields['min_num'].error_messages['invalid'])
            return ''

    def clean_max_num(self):
        if self.cleaned_data['max_num'] == '':
            return ''
        try:
            return float(self.cleaned_data['max_num'])
        except:
            raise forms.ValidationError(self.fields['max_num'].error_messages['invalid'])
            return ''

class Sample_Filter_Date_Form(forms.ModelForm):
    min_date = forms.CharField(
        max_length=50, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder':"min: yyyy-mm-dd", 'class':'input-large'}),
        error_messages={'invalid': "Please format: yyyy-mm-dd'"}
    )
    max_date = forms.CharField(
        max_length=50, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder':"max: yyyy-mm-dd", 'class':'input-large'}),
        error_messages={'invalid': "Please format: yyyy-mm-dd'"}
    )

    class Meta:
        model = SampleFilterPart
        fields = []

    def label(self):
        mod = self.instance
        return ' . '.join([mod.ref, mod.table, mod.filter_col])

    def clean_min_date(self):
        import datetime, time
        if self.cleaned_data['min_date'] == '':
            return ''
        try:
            data = self.cleaned_data['min_date']
            val = datetime.datetime.strptime(data, '%Y-%m-%d').date()
            tt = time.mktime(val.timetuple())
            return tt
        except:
            raise forms.ValidationError(self.fields['min_date'].error_messages['invalid'])
            return ''

    def clean_max_date(self):
        import datetime, time
        if self.cleaned_data['max_date'] == '':
            return ''
        try:
            data = self.cleaned_data['max_date']
            val = datetime.datetime.strptime(data, '%Y-%m-%d').date()
            tt = time.mktime(val.timetuple())
            return tt
        except:
            raise forms.ValidationError(self.fields['max_date'].error_messages['invalid'])
            return ''

class Table_Column_Data_Histogram_Form(forms.Form):
    hist_table_ref = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_table = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_column = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_type = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_numroundto = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput()) 
    hist_min_num = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_max_num = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_min_date = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_max_date = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_dateroundto = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput()) 
 
class Sample_Column_Data_Histogram_Form(forms.Form):
    hist_sample = forms.IntegerField(required=True, widget=forms.HiddenInput())
    hist_table_ref = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_table = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_column = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())
    hist_kind = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput())

class New_Filter_Form(forms.Form):
    new_filter_name = forms.CharField(required=False, max_length=100)
    new_filter_join = forms.CharField(required=False, max_length=200, widget=forms.HiddenInput())

 
class Add_To_Filter_Form(forms.Form):
    addto_filter_name = forms.ModelChoiceField(
        required=False, 
        queryset=SampleFilter.objects.all().order_by('-id'), 
        label='Add to filter:'
    )
    addto_filter_table_ref = forms.CharField(max_length=100, widget=forms.HiddenInput())
    addto_filter_table = forms.CharField(max_length=100, widget=forms.HiddenInput())
    addto_filter_column = forms.CharField(max_length=100, widget=forms.HiddenInput())
    addto_filter_type = forms.CharField(max_length=100, widget=forms.HiddenInput())
 
class New_Sample_Form(forms.Form):
    new_sample_name = forms.CharField(
        max_length=50,
        required=False # javascript validation
    )
    new_sample_trigger = forms.BooleanField(
        required=False, 
        widget=forms.HiddenInput(),
        initial=False
    )
    test_sample_trigger = forms.BooleanField(
        required=False, 
        widget=forms.HiddenInput(),
        initial=False
    )
 
class Retrieve_Sample_Form(forms.Form):
    sample = forms.IntegerField(
        required=True, 
        widget=forms.HiddenInput(),
    )
 
class Retrieve_OSample_Form(forms.Form):
    osample = forms.IntegerField(
        required=True, 
        widget=forms.HiddenInput(),
    )

class Browse_Sample_Form(forms.Form):
    sample = forms.ModelChoiceField(
        required=True, 
        label='Select a sample', 
        error_messages={'required': 'You must choose a sample'},
        queryset=Sample.objects.filter(status='Loaded').order_by('-id'), 
        widget=forms.Select(attrs={"onChange":"$('#choose_sample_form').submit();"})
    )
    mod_osample = forms.IntegerField(
        required=True, 
        widget=forms.HiddenInput(),
        initial = 0
    )

class Properties_Sample_Form(forms.Form):
    sample = forms.ModelChoiceField(
        required=True, 
        label='Select a sample', 
        error_messages={'required': 'You must choose a sample'},
        queryset=Sample.objects.filter(status='Loaded').order_by('-id'), 
        widget=forms.Select(attrs={"onChange":"$('#properties_sample_form').submit();"})
    )

class Comparisons_Sample_Form(forms.Form):
    sampleA = forms.ModelChoiceField(
        required=True, 
        label='Select sample A', 
        error_messages={'required': 'Next choose sample A'},
        queryset=Sample.objects.filter(status='Loaded').order_by('-id'), 
        widget=forms.Select(attrs={"onChange":"$('#comparisons_sample_form').submit();"})
    )
    sampleB = forms.ModelChoiceField(
        required=True, 
        label='Select sample B', 
        error_messages={'required': 'Next choose sample B'},
        queryset=Sample.objects.filter(status='Loaded').order_by('-id'), 
        widget=forms.Select(attrs={"onChange":"$('#comparisons_sample_form').submit();"})
    )

