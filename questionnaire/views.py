import json
import csv
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.core import serializers
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import FormConfig, FormData, EnrolledClients
from .forms import FormConfigForm
from .utilities import pick_random_clients


@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(request, 'questionnaire/dashboard.html')
    else:
        return redirect(reverse('form-listing'))


@login_required
def followup_day3(request):
    date_filter = datetime.now().date() - timedelta(days=3)
    selected_clients = pick_random_clients(EnrolledClients.objects.filter(delivery_date__exact=date_filter))
    if request.method == "POST" and request.is_ajax():
        field = request.POST.get('field')
        value = request.POST.get('value')
        if field == "called":
            EnrolledClients.objects.filter(id=int(request.POST.get('id'))).update(
                called=value
            )
        elif field == "available":
            EnrolledClients.objects.filter(id=int(request.POST.get('id'))).update(
                available=value
            )
        return HttpResponse(content_type="application/json")
    return render(
        request, 'questionnaire/followup_day3.html',
        {'selected_contacts': selected_clients, 'date': datetime.now().date()}
    )


@login_required
def followup_day7(request):
    min_dt = datetime.now().date() - timedelta(days=10)
    max_dt = datetime.now().date() - timedelta(days=7)
    clients = EnrolledClients.objects.filter(delivery_date__in=(min_dt, max_dt)).filter(came_day7=False)
    if request.method == "POST" and request.is_ajax():
        value = request.POST.get('value')
        if request.POST.get('field') == "came_day7":
            EnrolledClients.objects.filter(id=int(request.POST.get('id'))).update(
                came_day7=value
            )
        return HttpResponse(content_type="application/json")
    elif request.method == "GET" and request.is_ajax():
        picked_date = datetime.strptime(request.GET.get('datePicked'), "%m/%d/%Y").date()
        min_dt = picked_date - timedelta(days=10)
        max_dt = picked_date - timedelta(days=7)
        clients = EnrolledClients.objects.filter(delivery_date__in=(min_dt, max_dt)).filter(came_day7=False)
        response = serializers.serialize('json', clients)
        return HttpResponse(response, content_type="application/json")
    return render(
        request, 'questionnaire/followup_day7.html',
        {'clients': clients, 'date': datetime.now().date()}
    )


@login_required
def followup_day28(request):
    min_dt = datetime.now().date() - timedelta(days=33)
    max_dt = datetime.now().date() - timedelta(days=28)
    clients = EnrolledClients.objects.filter(delivery_date__in=(min_dt, max_dt)).filter(came_day28=False)
    if request.method == "POST" and request.is_ajax():
        value = request.POST.get('value')
        if request.POST.get('field') == "came_day28":
            EnrolledClients.objects.filter(id=int(request.POST.get('id'))).update(
                came_day28=value
            )
        return HttpResponse(content_type="application/json")
    elif request.method == "GET" and request.is_ajax():
        picked_date = datetime.strptime(request.GET.get('datePicked'), "%m/%d/%Y").date()
        min_dt = picked_date - timedelta(days=10)
        max_dt = picked_date - timedelta(days=7)
        clients = EnrolledClients.objects.filter(delivery_date__in=(min_dt, max_dt)).filter(came_day7=False)
        response = serializers.serialize('json', clients)
        return HttpResponse(response, content_type="application/json")
    return render(
        request, 'questionnaire/followup_day28.html',
        {'clients': clients, 'date': datetime.now().date()}
    )


@login_required
def form_listing(request):
    form_list = FormConfig.objects.all()
    return render(request, 'questionnaire/form_listing.html', {'form_list': form_list})


@login_required
def manage_form(request, slug=None):
    if not slug:
        formconfig = FormConfig()
        action = reverse('form-create')
    else:
        formconfig = get_object_or_404(FormConfig, slug=slug)
        action = reverse('form-update', kwargs={'slug': formconfig.slug})
    form = FormConfigForm(request.POST or None, instance=formconfig)
    if form.is_valid():
        saved_form = form.save()
        return redirect(reverse('form-editor', kwargs={'slug': saved_form.slug}))
    return render(request, 'questionnaire/form.html', {'form': form, 'action': action})


@login_required
def form_editor(request, slug):
    form = get_object_or_404(FormConfig, slug=slug)
    schema = json.dumps(form.schema)
    options = json.dumps(form.options)
    if request.method == "POST" and request.is_ajax():
        try:
            conf = json.loads(request.POST.get('conf'))
            form.schema = conf.pop('schema')
            form.options = conf.pop('options')
            form.save()
            response = {'message': 'form saved'}
            return HttpResponse(json.dumps(response), content_type="application/json")
        except AttributeError:
            response = {'message': 'Please provide a well formatted JSON object'}
            return HttpResponse(json.dumps(response), content_type="application/json")
    return render(request, 'questionnaire/form_editor.html', {'form': form, 'schema': schema, 'options': options})


@login_required
def data_listing(request, slug):
    form = get_object_or_404(FormConfig, slug=slug)
    data_forms = form.get_data()
    return render(request, 'questionnaire/data_listing.html', {'form': form, 'data_forms': data_forms})


@login_required
@csrf_exempt
def form_display(request, slug, uuid=None):
    form = get_object_or_404(FormConfig, slug=slug)
    if not uuid:
        dataform = FormData()
        data = json.dumps(dataform.data)
        action = reverse('data-create', kwargs={'slug': form.slug})
    else:
        dataform = form.formdata_set.get(uuid=uuid)
        data = json.dumps(dataform.data)
        action = reverse('data-update', kwargs={'slug': form.slug, 'uuid': dataform.uuid})
    form.options["form"]["attributes"]["action"] = action
    schema = json.dumps(form.schema)
    options = json.dumps(form.options)
    if request.method == "POST":
        dataform.data = request.POST
        dataform.form = form
        dataform.save()
        return redirect(reverse('data-listing', kwargs={'slug': form.slug}))
    return render(request, 'questionnaire/form_display.html', {
        'form': form, 'schema': schema, 'options': options, 'data': data, 'action': action
    })


@login_required
def export_form_data(request, slug):
    form = get_object_or_404(FormConfig, slug=slug)
    filled_forms = form.get_data()
    if filled_forms:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s_%s.csv"' % (
            '_'.join(form.name.lower().split(' ')),
            datetime.now().strftime("%Y%m%d_%H%M%S")
        )

        header = filled_forms[-1]['data'].keys() + ['time']
        writer = csv.DictWriter(response, header)
        writer.writeheader()
        writer.writerows([filled_form['data'] for filled_form in filled_forms])

        return response
