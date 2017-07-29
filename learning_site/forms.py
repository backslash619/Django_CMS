from django import forms


def must_be_empty(value):
    if value:
        raise forms.ValidationError("should be empty")


# here we create the classes as it automatically converts it into html etc.

class SuggestionForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    verify_email = forms.EmailField(label='Please verify your email address.')
    suggest = forms.CharField(widget=forms.Textarea)
    honeypot = forms.CharField(required=False,
                               widget=forms.HiddenInput,
                               label='Leave Empty',
                               validators=[must_be_empty])

    # to verify the email we use the clean method as it clean the whole form at once

    def clean(self):
        cleaned_data = super().clean()
        # calls then clean method on super() content

        # email = cleaned_data['email']
        # or
        email = cleaned_data.get('email')
        verify = cleaned_data.get('verify_email')

        if email != verify:
            raise forms.ValidationError(
                "You've to enter the same email in both the fields."
            )

            # we can use custom validator instead of Maxlengthvalidator

            # so when we check for the is_valid in the if condition it;s going to check all the fields and clean_anyfieldname
            # going to run automatically
            # this is just cleaninig one field
            # as this is not the best idea instead of this  we can use the core django feature validators

            # def clean_honeypot(self):
            # honeypot = self.cleaned_data['honeypot']
            # if len(honeypot):
            #     raise forms.ValidationError(
            #         'honeypot should be left empty!!'
            #     )
            # return honeypot
