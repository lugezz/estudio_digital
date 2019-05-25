from django import forms
from contacts.models import Contact
from common.models import Comment, Attachments


class ContactForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}
        self.fields['description'].widget.attrs.update({
            'rows': '6'})

        for key, value in self.fields.items():
            if key == 'phone':
                value.widget.attrs['placeholder'] = "+54-351-456-7890"
            elif key == 'description':
                value.widget.attrs['placeholder'] = "Descripción"
            else:
                value.widget.attrs['placeholder'] = value.label

    class Meta:
        model = Contact
        fields = (
            'first_name',
            'last_name', 'email',
            'phone', 'address', 'description'
        )


class ContactCommentForm(forms.ModelForm):
    comment = forms.CharField(max_length=64, required=True)

    class Meta:
        model = Comment
        fields = ('comment', 'contact', 'commented_by')
