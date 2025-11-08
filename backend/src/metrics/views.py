from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def metrics(request):
    metrics = Members.objects.all().values()
    template = loader.get_template('memberList.html')
    context = {
        'members': members,
    }
    return HttpResponse(template.render(context, request))