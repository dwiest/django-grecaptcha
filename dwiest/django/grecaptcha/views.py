from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import FormView
from .forms import GRecaptchaForm

class GRecaptchaView(FormView):
  template_name = "grecaptcha/index.html"
  success_url = '.'
  form_class = GRecaptchaForm
  page_name = 'Google reCAPTCHA'

  def __init__(self, *args, **kwargs):
    self.response_dict = {
      'action': GRecaptchaForm.action,
      'page_name': self.page_name,
      'site_key': settings.GOOGLE_RECAPTCHA_SITE_KEY
    }

    return super(FormView, self).__init__(*args, **kwargs)

  def get(self, request, *args, **kwargs):
    print("GRecaptchaView.get()")
    form = GRecaptchaForm()
    self.response_dict['form'] = form
    return render(request, self.template_name, self.response_dict)

  def post(self, request, *args, **kwargs):
    print("GRecaptchaView.post()")
    form = GRecaptchaForm(request.POST)
    self.response_dict['form'] = form
    if form.is_valid():
      request.session['risk_score'] = form.risk_score
      return HttpResponseRedirect(request.path)
    else:
      return render(request, self.template_name, self.response_dict)
