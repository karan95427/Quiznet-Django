from django import forms
class TopicForm(forms.Form):
    topic=forms.CharField(label="Enter a Topic",max_length=100, widget=forms.TextInput(attrs={"class":"form-input"}))
   