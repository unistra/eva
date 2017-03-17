from django import forms


class FileUploadForm(forms.Form):
    """File upload form."""
    file = forms.FileField()
