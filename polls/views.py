from django.http import HttpResponse
from django.shortcuts import render

from polls.pdf import MakePdf


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def generate_pdf(request):

    # return HttpResponse("Hello, world. PDF")

    pdf = MakePdf.print_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    content = "attachment; filename=pols.pdf"
    response['Content-Disposition'] = content
    return response

