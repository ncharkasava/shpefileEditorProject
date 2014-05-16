# Views for login, logout, registration, authentication check and contact form
# and renders for shared pages - help, contact, about
# Inplemented based on http://www.mikesdjangotutorials.co.uk/ 

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.core.context_processors import csrf
from shapeEditor.editor.forms import MyRegistrationForm
from shapeEditor.editor.forms import ContactForm
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.mail import send_mail
import logging

logr = logging.getLogger(__name__)


# user login
def login(request):
    c = {}
    c.update(csrf(request))    
    return render_to_response('login.html', c)
    
# user authentification check 
def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/editor')
    else:
        return HttpResponseRedirect('/editor/invalid')
    
# render for user login - redirect to home page to uploaded shapefiles
def loggedin(request):
    return render_to_response('list_shapefiles.html', 
                              {'full_name': request.user.username})

# render for invalid login
def invalid_login(request):
    return render_to_response('invalid_login.html')

# user logout 
def logout(request):
    auth.logout(request)
    return render_to_response('list_shapefiles.html', 
                              {'full_name': request.user.username})
# render for help page
def help(request):
    userid = request.user
    return render_to_response('help.html',
                             {'full_name': request.user.username})

# render for about page
def about(request):
    userid = request.user
    return render_to_response('about.html',
                             {'full_name': request.user.username})

# new user registration
def register_user(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/editor/register_success')
        
    else:
        form = MyRegistrationForm()
    args = {}
    args.update(csrf(request))
    
    args['form'] = form
    
    return render_to_response('register.html', args)


def register_success(request):
    return render_to_response('register_success.html')


# contact form page
def contact(request):
    userid = request.user
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
             subject = request.POST.get('subject', '')
             sender = request.POST.get('sender', '')
             message = request.POST.get('message', '')
             message_text = "Sender: " + sender + "\nMessage: " + message
             send_mail(subject, message_text, sender, ['ncharkasava@gmail.com'], fail_silently=False)
             return render_to_response('done.html',
                             {'full_name': request.user.username})
 
    else:
        form = ContactForm()
    args = {}
    args.update(csrf(request))
    
    args['form'] = form
    return render_to_response('contact.html',
                             {'full_name': request.user.username})



class ContactWizard(SessionWizardView):
    template_name = "contact_form.html"
    
    def done(self, form_list, **kwargs):
        form_data = process_form_data(form_list)
        
        return render_to_response('done.html', {'form_data': form_data})

# processing contact form
def process_form_data(form_list):
    form_data = [form.cleaned_data for form in form_list]
    
    logr.debug(form_data[0]['subject'])
    logr.debug(form_data[1]['sender'])
    logr.debug(form_data[2]['message'])
    message_text = "Sender: " + form_data[1]['sender'] + "\nMessage: " + form_data[2]['message']
    
    send_mail(form_data[0]['subject'], 
              message_text, form_data[1]['sender'],
              ['ncharkasava@gmail.com'], fail_silently=False)
    
    return form_data




