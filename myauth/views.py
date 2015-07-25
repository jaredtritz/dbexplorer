from django.shortcuts import render_to_response, render, redirect

# Create your views here.

def test_view(request):
    return render(request, 'transfer/base_transfer.html', {})

def mylogout_view(request):
    return HttpResponseRedirect("https://weblogin.umich.edu/cgi-bin/logout")
