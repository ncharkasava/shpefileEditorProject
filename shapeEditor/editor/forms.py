from django import forms
from shapeEditor.shared.models import Shapefile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


CHARACTER_ENCODINGS = [("ascii", "ASCII"),
			("latin1", "Latin-1"),
			("utf8", "UTF-8")]

class ImportShapefileForm(forms.Form):
    import_file = forms.FileField(label="Select a Zipped Shapefile")
    character_encoding = forms.ChoiceField(choices=CHARACTER_ENCODINGS, initial="utf8")

class ChangeAttributeValueForm(forms.Form):
    attribute_value = forms.TextInput()


class AddAttributeValueForm(forms.Form):
 #   attribute = forms.ModelChoiceField(queryset=Shapefile.objects.get(id=shapefile_id))
    attribute_value = forms.TextInput()

class MyRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super(MyRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        # user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
            
        return user
    

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    sender = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

class ContactForm1(forms.Form):
    subject = forms.CharField(max_length=100)
    
class ContactForm2(forms.Form):
    sender = forms.EmailField()

class ContactForm3(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
    

