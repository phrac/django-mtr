from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext

from documents.models import Document
from documents.forms import AttachDocumentForm
from reports.models import Report, ReportDocument

def documents_index(request):
    documents = Document.objects.all()
    
    return render_to_response('documents/documents_index.html',
                              {'documents': documents,
                              },
                              context_instance=RequestContext(request))

def document(request, uuid):
    document = Document.objects.get(uuid=uuid)

    reports = ReportDocument.objects.filter(document=document)
    attach_document_form = AttachDocumentForm(None)
    return render_to_response('documents/document.html',
                              {'document': document,
                               'reports': reports,
                               'attach_document_form': attach_document_form,
                              },
                              context_instance=RequestContext(request))

def email_document(request):
    doc_id = request.POST.get('doc-id', None)
    report_id = request.POST.get('report-id', None)
    recipient = request.POST.get('recipient', None)

    doc = Document.objects.get(id=doc_id)
    report = Report.objects.get(id=report_id)
    subject = "%s for lot # %s" % (doc.type, report.lot_number)
    body = "See attached document for the %s for lot # %s" % (doc.type, report.lot_number)
    body += "\n\nLot Number: %s" % report.lot_number
    body += "\nPart Number: %s" % report.part_number
    body += "\nDescription: %s" % report.part_number.description

    email = EmailMessage(subject, body, 'mtr@tsamfg.com', [recipient], headers={'Reply-To': 'derek.m@tsamfgomaha.com'})

    email.attach("MTR_%s.pdf" % report.lot_number, doc.file.read(), 'application/pdf')
    email.send()
    messages.success(request, "Email sent to %s" % recipient)
    return HttpResponseRedirect(reverse('reports.views.report', args=[str(report.lot_number)]))
    
def attach_document(request):
    doc_id = request.POST.get('document_id', None)
    
    docform = AttachDocumentForm(request.POST)
    if docform.is_valid():
        doc = Document.objects.get(id=doc_id)
        lot_number = docform.cleaned_data['lot_number']
        rd = ReportDocument(report=lot_number, document=doc, primary_document=docform.cleaned_data['primary'])
        rd.save()
        lot_number.save()
        messages.success(request, 'Document attachment successful.')
        return HttpResponseRedirect(reverse('documents.views.document', args=[str(doc.uuid)]))
    

    

